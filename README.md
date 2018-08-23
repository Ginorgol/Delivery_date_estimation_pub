# Delivery_date_estimation_pub



- This project aims to predict the delivery date for the a order placed depending various factors ,the main factor being the time returned by google maps api.
- It tries to mimic a courier delivery service ,with various hubs placed to map requirements pan India.
- It Makes a fully connected graph with weights found out by machine learning on various dummy variables which can be modified 
depending upon your use case.
- It then finds out the nearest warehouse(W_seller) to seller address,and the nearest warehouse to destination address(W_customer).
- It then finds out the shortest path using Djisktra algorithm(W_seller,W_customer to finally get the Estimated time of arrival
