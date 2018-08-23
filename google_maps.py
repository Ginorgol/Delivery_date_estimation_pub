import googlemaps
from datetime import datetime,timedelta
from collections import defaultdict
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split
from djisktra import Heap,Graph
from random import randint
import datetime as dt
gmaps = googlemaps.Client(key="AIzaSyDu7i1Zy6xwtRvCiH4cCqOCkouPju4rk2Y")
now = datetime.now()

#try to build a graph with the centres you have

list_of_warehouse=["Mumbai","Banglore","Hyderabad","Chennai","Ahmedabad",
					"Jaipur","Gurugram","Pune","Delhi","Kolkata"]
ETA=0
warehouse_id={
	0:"Mumbai",
	1:"Banglore",
	2:"Hyderabad",
	3:"Chennai",
	4:"Ahmedabad",
	5:"Jaipur",
	6:"Gurugram",
	7:"Pune",
	8:"Delhi",
	9:"Kolkata"
}
warehouse_id_rev={
	"Mumbai":0,
	"Banglore":1,
	"Hyderabad":2,
	"Chennai":3,
	"Ahmedabad":4,
	"Jaipur":5,
	"Gurugram":6,
	"Pune":7,
	"Delhi":8,
	"Kolkata":9
}
hub_average_delay={
	"Mumbai":5,
	"Banglore":3,
	"Hyderabad":4,
	"Chennai":5,
	"Ahmedabad":2,
	"Jaipur":1,
	"Gurugram":2,
	"Pune":4,
	"Delhi":5,
	"Kolkata":5
}
hub_rating={ #out of 5
	"Mumbai":5,
	"Banglore":3,
	"Hyderabad":4,
	"Chennai":4,
	"Ahmedabad":3,
	"Jaipur":2,
	"Gurugram":3,
	"Pune":2,
	"Delhi":4,
	"Kolkata":4	
}
major_hub=["Delhi","Mumbai","Kolkata","Chennai"]
national_holidays=['26/1','15/8','2/10']
weather_delay={
	"rainy":5,
	"sunny":1,
	"normal":0,
	"snow":10,
	"storm":20
}
weather=["rainy","sunny","normal","snow","storm"]
weather_d=weather_delay[weather[randint(0,4)]]

class Warehouse:
	def __init__(self,place,capacity,wait_time):
		self.place=place
		self.capacity=capacity
		self.wait_time=wait_time
	def update_cap(val):
		self.capacity+=val


class Delivery_fac:
	def __init__(self,rating,average_delay,capacity):
		self.rating=rating
		self.average_delay=average_delay
		self.capacity=capacity
	def update_cap(val):
		self.capacity+=val


class Delivery_object:
	def __init__(self,volume,weight,is_delicate):
		self.volume=volume
		self.weight=weight
		self.is_delicate=is_delicate

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def print_graph(graph):
	for src in graph:
		print(warehouse_id_rev[src])
		print("")
		for dest in graph[src]:
			print(warehouse_id_rev[dest],end=" ")

def time_taken_to_weight(time_taken): #returns total time in hours
	temp_list=time_taken.split(" ")
	#temp_list=[" ".join(temp_list[i:i+2]) for i in range(0, len(temp_list), 2)]
	time_dict={}
	for idx,temp in enumerate(temp_list):
		#print(temp)
		if(is_number(temp)):
			time_dict[temp_list[idx+1].replace("s","")]=int(temp)
	total_time=0
	#print(time_dict)
	for time_dur,val in time_dict.items():
		if(time_dur=="day"):
			total_time+=(24*time_dict[time_dur])
		elif(time_dur=="minute" or time_dur=="min"):
			total_time+=1
		else:
			total_time+=time_dict[time_dur]

	return total_time


def find_lat_long():
	lat_long_dict=dict()
	for warehouse in list_of_warehouse:
		geocode_result = gmaps.geocode(warehouse)
		lat=geocode_result[0]['geometry']['location']['lat']
		lng=geocode_result[0]['geometry']['location']['lng']
		lat_long_dict[warehouse]=(lat,lng)
	return lat_long_dict




def add_lat_long(address):
	geocode_result=gmaps.geocode(address)
	lat=geocode_result[0]['geometry']['location']['lat']
	lng=geocode_result[0]['geometry']['location']['lng']
	return (lat,lng)


def initialise_model():
	dataset=pd.read_csv("data.csv")

	X=dataset.iloc[:,:-1].values
	Y=dataset.iloc[:,11].values
	X_train,X_test,y_train,y_test=	train_test_split(X,Y,test_size=0.2,random_state=0)


	#simple linear regression
	regressor =LinearRegression()
	regressor.fit(X_train,y_train)

	#random forest regressor
	regressor_rf=RandomForestRegressor()
	regressor_rf.fit(X_train,y_train)
	return regressor,regressor_rf

def final_weight(df,regressor,regressor_rf):
	return (regressor_rf.predict(df)+(1.2*(regressor.predict(df))))/2.2

def to_num(dist_str):
	temp=dist_str.split(' ')
	final_dist=float(temp[0].replace(",",""))
	return final_dist

def seller_to_src_warehouse(seller_add,seller_wait_time,lat_long_dict):
	#seller_wait_time is in hours
	#find nearest warehouse
	#try finding by name just and put it in try and except
	distances_from_warehouse={}
	time_till_warehouse={}
	for warehouse in list_of_warehouse:
		try:
			current_time=datetime.now()
			depart_time=current_time+timedelta(hours=seller_wait_time)
			directions_result = gmaps.directions(origin=add_lat_long(seller_add),destination=lat_long_dict[warehouse],
						                                     mode="transit",
						                                     departure_time=depart_time)#add wait time if the time is not working hours or capacity is full
			req=directions_result[0]
			req=req['legs']
			req=req[0]
			departure_time=req['departure_time']['text']
			arrival_time=req['arrival_time']['text']
			distance=req['distance']['text']
			time_taken=req['duration']['text']
			weight=time_taken_to_weight(time_taken)
			#print(warehouse,time_taken)
			time_till_warehouse[warehouse]=weight
			distances_from_warehouse[warehouse]=distance

		except:
			continue


	for key,dist in distances_from_warehouse.items():
		distances_from_warehouse[key]=to_num(dist)
	print(distances_from_warehouse)
	#print(time_till_warehouse)
	temp=sorted(distances_from_warehouse, key=distances_from_warehouse.get)
	source_warehouse=temp[0]
	time_till_nearest_warehouse=time_till_warehouse[source_warehouse]
	return source_warehouse,time_till_nearest_warehouse


def customer_to_nearest_warehouse(customer_add,source_warehouse,lat_long_dict):
	distances_from_warehouse={}
	time_till_warehouse={}
	for warehouse in list_of_warehouse:
		try:
			directions_result = gmaps.directions(origin=add_lat_long(customer_add),destination=lat_long_dict[warehouse],
						                                     mode="transit",
						                                     departure_time=now)
			req=directions_result[0]
			req=req['legs']
			req=req[0]
			departure_time=req['departure_time']['text']
			arrival_time=req['arrival_time']['text']
			distance=req['distance']['text']
			time_taken=req['duration']['text']
			weight=time_taken_to_weight(time_taken)
			time_till_warehouse[warehouse]=weight
			distances_from_warehouse[warehouse]=distance
		except:
			continue


	for key,dist in distances_from_warehouse.items():
		distances_from_warehouse[key]=to_num(dist)
	print(distances_from_warehouse)
	#print(time_till_warehouse)
	temp=sorted(distances_from_warehouse, key=distances_from_warehouse.get)
	destination_warehouse=temp[0]
	time_till_nearest_warehouse=time_till_warehouse[source_warehouse]
	return destination_warehouse,time_till_warehouse

def final_warehouse_to_customer(customer_add,final_warehouse,warehouse_arrival_wait,lat_long_dict):
	try:
		current_time=datetime.now()
		print(warehouse_arrival_wait)
		depart_time=current_time+ timedelta(hours=warehouse_arrival_wait)
		directions_result = gmaps.directions(origin=add_lat_long(customer_add),destination=lat_long_dict[final_warehouse],
						                                     mode="transit",
						                                     departure_time=depart_time)
	
		#print(directions_result)
		req=directions_result[0]
		req=req['legs']
		req=req[0]
		departure_time=req['departure_time']['text']
		arrival_time=req['arrival_time']['text']
		distance=req['distance']['text']
		time_taken=req['duration']['text']
		weight=time_taken_to_weight(time_taken)
		return weight
	except:
		return None





# source_warehouse,time_till_warehouse=seller_to_src_warehouse(SELLER_ADDRESS,10)
# destination_warehouse,time_till_warehouse_customer=customer_to_nearest_warehouse(CUSTOMER_ADDRESS)
# ETA+=time_till_warehouse
# print(source_warehouse)
# print(time_till_warehouse)
# print(destination_warehouse)


# source ="Delhi"
# destination="Hyderabad"
# directions_result = gmaps.directions(origin="Delhi",destination="Hyderabad",mode="transit",departure_time=now,traffic_model="pessimistic")#add wait time if the time is not working hours or capacity is full
# req=directions_result[0]
# req=req['legs']
# req=req[0]
# departure_time=req['departure_time']['text']
# arrival_time=req['arrival_time']['text']
# distance=req['distance']['text']
# time_taken=req['duration']['text']
# weight=time_taken
# m_delay=0
# nh_delay=0
# weekend_adv=0
# if(source in major_hub and distance in major_hub):
# 	m_delay=5
# s_id=warehouse_id_rev[source]
# e_id=warehouse_id_rev[destination]
# if((str(now.day)+'/'+str(now.month)) in national_holidays):
# 	nh_delay=24
# st_delay=hub_average_delay[source]
# en_delay=hub_average_delay[destination]
# hub_rating_delay=0
# if(hub_rating[source]+hub_rating[destination]<8 and hub_rating[source]+hub_rating[destination]>5): 
# 	hub_rating_delay=4
# elif(hub_rating[source]+hub_rating[destination]<=5):
# 	hub_rating_delay=7
# else:
# 	hub_rating_delay=0
# weather_delay=weather_delay[weather[randint(0,4)]]
# weekno = departure_time.datetime.today().weekday()
# if(weekno>=5):
# 	weekend_adv=-3
# d={'Distance':[distance],'Start_ID':[s_id],'End_ID':[e_id],'G MAp Time':[weight],'M HUB Delay':[m_delay],'Weekend Advantage':[weekend_adv],'N H Delay':[nh_delay],'Start Delay':[st_delay],'End Delay':[en_delay],'Rating Delay':[hub_rating_delay],'weather Delay':[weather_delay]}
# df=pd.DataFrame(data=d)
# weight=final_weight(df,regressor,regressor_rf)
# print(weight)

def make_graph(safe_threshold):
	graph=Graph(10)
	temp_graph=defaultdict(list)
	regressor,regressor_rf=initialise_model()
	for source in list_of_warehouse:
		for destination in list_of_warehouse:
			if(source==destination):
				weight=0
				temp_graph[source].append((destination,weight))
				graph.addEdge(warehouse_id_rev[source],warehouse_id_rev[destination],0)
			else:
				try:
					directions_result = gmaps.directions(lat_long_dict[source],
					                                     lat_long_dict[destination],
					                                     mode="transit",
					                                     departure_time=now)#add wait time if the time is not working hours or capacity is full
					req=directions_result[0]
					req=req['legs']
					req=req[0]
					departure_time=req['departure_time']['text']
					arrival_time=req['arrival_time']['text']
					distance=req['distance']['text']
					time_taken=req['duration']['text']
					weight=time_taken_to_weight(time_taken)
					# ML architecture starts 
					m_delay=0
					nh_delay=0
					weekend_adv=0
					if(source in major_hub and distance in major_hub):
						m_delay=5
					s_id=warehouse_id_rev[source]
					e_id=warehouse_id_rev[destination]
					if((str(now.day)+'/'+str(now.month)) in national_holidays):
						nh_delay=24
					st_delay=hub_average_delay[source]
					en_delay=hub_average_delay[destination]
					hub_rating_delay=0
					if(hub_rating[source]+hub_rating[destination]<8 and hub_rating[source]+hub_rating[destination]>5): 
						hub_rating_delay=4
					elif(hub_rating[source]+hub_rating[destination]<=5):
						hub_rating_delay=7
					else:
						hub_rating_delay=0
					weather_d=weather_delay[weather[randint(0,4)]]
					weekno = dt.datetime.today().weekday()
					if(weekno>=5):
						weekend_adv=-3
					#print(distance)
					temp_distance=distance.split(' ')
					#print(temp_distance)
					final_dist=temp_distance[0].replace(",","")
					#print(final_dist)
					d={'Distance':[final_dist],'Start_ID':[s_id],'End_ID':[e_id],'G MAp Time':[weight],'M HUB Delay':[m_delay],'Weekend Advantage':[weekend_adv],'N H Delay':[nh_delay],'Start Delay':[st_delay],'End Delay':[en_delay],'Rating Delay':[hub_rating_delay],'weather Delay':[weather_d]}
					#print(d)
					df=pd.DataFrame(data=d)
					weight=final_weight(df,regressor,regressor_rf)
					# ML arighitecture ends
					temp_tup=(source,destination,weight[0],distance)
					print(temp_tup)
					tup=(destination,weight[0])
					temp_graph[source].append(tup)
					graph.addEdge(warehouse_id_rev[source],warehouse_id_rev[destination],weight[0])
				except:
					try:
						directions_result = gmaps.directions(source,
						                                     destination,
						                                     mode="transit",
						                                     departure_time=now)#add wait time if the time is not working hours or capacity is full
						req=directions_result[0]
						req=req['legs']
						req=req[0]
						departure_time=req['departure_time']['text']
						arrival_time=req['arrival_time']['text']
						distance=req['distance']['text']
						time_taken=req['duration']['text']
						weight=time_taken_to_weight(time_taken)
						#ML architecture starts 
						m_delay=0
						nh_delay=0
						weekend_adv=0
						if(source in major_hub and distance in major_hub):
							m_delay=5
						s_id=warehouse_id_rev[source]
						e_id=warehouse_id_rev[destination]
						if((str(now.day)+'/'+str(now.month)) in national_holidays):
							nh_delay=24
						st_delay=hub_average_delay[source]
						en_delay=hub_average_delay[destination]
						hub_rating_delay=0
						if(hub_rating[source]+hub_rating[destination]<8 and hub_rating[source]+hub_rating[destination]>5): 
							hub_rating_delay=4
						elif(hub_rating[source]+hub_rating[destination]<=5):
							hub_rating_delay=7
						else:
							hub_rating_delay=0
						weather_d=weather_delay[weather[randint(0,4)]]
						weekno = dt.datetime.today().weekday()
						if(weekno>=5):
							weekend_adv=-3
						#print(distance)

						temp_distance=distance.split(' ')
						#print(temp_distance)
						final_dist=temp_distance[0].replace(",","")
						#print(final_dist)
						d={'Distance':[final_dist],'Start_ID':[s_id],'End_ID':[e_id],'G MAp Time':[weight],'M HUB Delay':[m_delay],'Weekend Advantage':[weekend_adv],'N H Delay':[nh_delay],'Start Delay':[st_delay],'End Delay':[en_delay],'Rating Delay':[hub_rating_delay],'weather Delay':[weather_d]}
						df=pd.DataFrame(data=d)
						#print(d)
						#print(regressor.predict(df))
						weight=final_weight(df,regressor,regressor_rf)


						# # ML arighitecture ends

						temp_tup=(source,destination,weight[0],distance)
						print(temp_tup)
						tup=(destination,weight[0])
						temp_graph[source].append(tup)

						graph.addEdge(warehouse_id_rev[source],warehouse_id_rev[destination],weight[0])

					except:
						try:
							weight_list=[x[1] for x in temp_graph[destination] if x[0]==source]
							weight=weight_list[0]
							weight+=safe_threshold
							temp_tup=(source,destination,weight)
							print(temp_tup)
							tup=(destination,weight)
							temp_graph[source].append(tup)
							graph.addEdge(warehouse_id_rev[source],warehouse_id_rev[destination],weight)
						except:
							graph.addEdge(warehouse_id_rev[source],warehouse_id_rev[destination],100)
							print("Major error use default value")#construct default values
						
				
	return graph,temp_graph

# safe_threshold=5
# graph,temp_graph=make_graph(10)
# #call here
# shortest_route_time=graph.dijkstra(warehouse_id_rev[source_warehouse],warehouse_id_rev[destination_warehouse])
# ETA+=shortest_route_time
# destination_warehouse_to_customer=final_warehouse_to_customer(CUSTOMER_ADDRESS,destination_warehouse,ETA)
# if destination_warehouse_to_customer==None:
# 	destination_warehouse_to_customer=time_till_warehouse_customer[destination_warehouse]
# ETA+=destination_warehouse_to_customer
# print(ETA)


def main(start_add,end_add):
	print("in main")
	CUSTOMER_ADDRESS=start_add
	SELLER_ADDRESS=end_add
	print("here also ")
	lat_long_dict=find_lat_long()
	print(lat_long_dict)
	ETA=0
	safe_threshold=5
	source_warehouse,time_till_warehouse=seller_to_src_warehouse(SELLER_ADDRESS,10,lat_long_dict)
	print(source_warehouse)
	destination_warehouse,time_till_warehouse_customer=customer_to_nearest_warehouse(CUSTOMER_ADDRESS,source_warehouse,lat_long_dict)
	print(destination_warehouse)
	ETA+=time_till_warehouse
	graph,temp_graph=make_graph(10)
	shortest_route_time=graph.dijkstra(warehouse_id_rev[source_warehouse],warehouse_id_rev[destination_warehouse])
	ETA+=shortest_route_time
	destination_warehouse_to_customer=final_warehouse_to_customer(CUSTOMER_ADDRESS,destination_warehouse,ETA,lat_long_dict)
	if destination_warehouse_to_customer==None:
		destination_warehouse_to_customer=time_till_warehouse_customer[destination_warehouse]
	ETA+=destination_warehouse_to_customer
	ETA+=5
	return ETA

