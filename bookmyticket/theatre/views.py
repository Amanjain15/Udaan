from django.shortcuts import render

from .models import *
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
# import keys
import json
import datetime

@csrf_exempt
def add_screen(request):
	response_json = {}
	if request.method == 'POST' :
		try:
			name=request.POST.get('name')
			seat_info=str(request.POST.get('seatInfo'))
			seat_info=json.loads(seat_info)
			screen_instance=ScreenData.objects.filter(name=name)
			if screen_instance.exists() :
				screen_instance=ScreenData.objects.get(name=name)
			else :	
				screen_instance=ScreenData.objects.create(
															name=name,
															row_num=0,
														)
			try:
				for row_name,data in seat_info.items():
					seat_num=data['numberOfSeats']
					aisle_seats=data['aisleSeats']
					row_instance=RowData.objects.filter(name=row_name,screen=screen_instance)
					if row_instance.exists():
						row_instance=RowData.objects.get(name=row_name,screen=screen_instance)
						setattr(row_instance,'seat_num',row_instance.seat_num + seat_num )
						row_instance.save()
					else :
						row_instance=RowData.objects.create(
															name=row_name,
															seat_num=seat_num,
															screen=screen_instance,
															)
						print "Row Instance Created"
					row_num=screen_instance.row_num + 1
					setattr(screen_instance,'row_num',row_num)
					screen_instance.save()
					for num in range(0,seat_num):
						is_aisle=False
						if num in aisle_seats:
							is_aisle=True
						seat_instance=SeatData.objects.create(
															seat_no=num,
															aisle_seat=is_aisle,
															row=row_instance,
															)

				response_json['success']=True
				response_json['message']='Screen Successfully Created'
			except Exception as e:
				response_json['success']=False
				response_json['message']=str(e)
				print str(e)
		except Exception as e:
			response_json['success']=False
			response_json['message']=str(e)
			print str(e)
	return JsonResponse(response_json)

def resolve_url(request,id):
	response_json={}
	if request.method == 'POST':
		response_json=reserve_tickets(request,id)
	else:
		response_json=available_seats(request,id)
	return JsonResponse(response_json)


def reserve_tickets(request,screen_name):
	response_json = {}
	if request.method == 'POST':
		try:
			seat_data=str(request.POST.get('seats'))
			seat_data=json.loads(seat_data)
			screen_data=ScreenData.objects.get(name=str(screen_name))
			time=str(datetime.datetime.now())
			time=time[11:23]
			transaction_id=str(screen_name)+'_'+str(len(seat_data))+'_'+time
			response_json['success']=True
			for row_name,data in seat_data.iteritems():
				row_data=RowData.objects.get(name=row_name,screen=screen_data)
				for num in data:
					seat_datas=SeatData.objects.get(seat_no=num,row=row_data)
					if seat_datas.reserved == True :
						response_json['success']=False
						response_json['message']="Sceen Name : "+str(screen_name)+", Row Name : "+str(row_name)+", Seat Num : "+str(num) + ", Status : Already Booked"
						break
			if response_json['success'] == True :
				print seat_data
				for row_name,data in seat_data.iteritems():
					print row_name,data
					row_data=RowData.objects.get(name=row_name,screen=screen_data)
					for num in data:
						seat_datas=SeatData.objects.get(seat_no=num,row=row_data)
						setattr(seat_datas,'reserved',True)
						seat_datas.save()
						reservation_data=ReservationData.objects.create(
																		transaction_id=str(transaction_id),
																		seat_data=seat_datas,
																		)
			if response_json['success'] == True :
				response_json['message'] = "Your Transaction ID is : "+ str(transaction_id)
		except Exception as e:
			response_json['success']=False
			response_json['message']=str(e)
			print str(e)
	return (response_json)

def available_seats(request,screen_name):
	response_json={}
	if request.method == 'GET' :
		status=str(request.GET.get('status'))
		if status == 'unreserved':
			try:
				screen_data=ScreenData.objects.get(name=str(screen_name))
				row_list=RowData.objects.filter(screen=screen_data)
				temp={}
				for row_data in row_list:
					seat_list=SeatData.objects.filter(row=row_data,reserved=False)
					seat_arr=[]
					for o in seat_list:
						seat_arr.append(o.seat_no)
					temp[row_data.name]=seat_arr
				response_json['seats']=temp
				response_json['success']=True
				response_json['message']="HTTP Status : 200"
			except Exception as e:
				response_json['success']=False
				response_json['message']=str(e)
				print str(e)
		else :
			response_json=available_contiguous_seats(request,screen_name)

	return (response_json)


def available_contiguous_seats(request,screen_name):
	response_json={}
	if request.method == 'GET' :
		try:
			num_seats=int(request.GET.get('numSeats'))
			choice=str(request.GET.get('choice'))
			seat_id=int(choice[1:])
			screen_data=ScreenData.objects.get(name=str(screen_name))
			row_data=RowData.objects.get(screen=screen_data,name=choice[:1])
			choice_seat=SeatData.objects.get(row=row_data,seat_no=seat_id)

			if choice_seat.reserved == True:
				response_json['success']=False
				response_json['message']="Selected Seat Already Booked" 
				return JsonResponse(response_json)

			seat_list=SeatData.objects.filter(row=row_data,reserved=False)
			is_before_aisle = -1
			is_after_aisle=len(seat_list)
			temp=[]
			for s in seat_list:
				if s.seat_no < seat_id :
					if s.aisle_seat == True:
						is_before_aisle = s.seat_no
						temp=[]
					temp.append(s.seat_no)
				elif s.seat_no == seat_id :
					temp.append(s.seat_no)
					if s.aisle_seat == True:
						if is_before_aisle == -1 :
							is_before_aisle = s.seat_no
							temp=[]
							temp.append(s.seat_no)
						else :
							is_after_aisle = s.seat_no
							break
				else :
					temp.append(s.seat_no)
					if s.aisle_seat == True:
						is_after_aisle = s.seat_no
						break

			if len(temp) >= num_seats :
				start= -1
				n=len(temp)
				for x in xrange(0,n):
					req=temp[x] + num_seats - 1
					if temp[x] <= seat_id and req >= seat_id and req <= temp[n-1]:
						num=1
						for y in xrange(x+1,x + num_seats):
							if temp[y] == temp[y-1] + 1:
								num=num+1
							else : 
								break
						if num == num_seats:
							start=temp[x]
				if start == -1 :
					response_json['success']=False
					response_json['message']="Error : No Contigous Seats Available at the Spot ! "
				else :
					arr=[]
					for start in xrange(start,start+num_seats):
						arr.append(start)
					temp_json={}
					temp_json[row_data.name]=arr
					response_json['availableSeats']=temp_json
					response_json['success']=True
					response_json['message']="Successfull"
					print response_json
					return (response_json)
			else :
				response_json['success']=False
				response_json['message']="Error : No Contigous Seats Available at the Spot ! "
		except Exception as e:
			response_json['success']=False
			response_json['message']=str(e)
			print str(e)
	print response_json
	return (response_json)
	