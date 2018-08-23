SELECT o.order_id,o.order_name,u.username from orders as o AND user as u where o.(?)= u.(?)",("orders.order_id","user.id

	

select order_name from orders where est_delivery <= datetime('now','+ 7 day')  AND user_id= "+ str(current_user.id)+" order by est_delivery asc


select order_name from orders where est_delivery <= '2018-08-26' AND user_id = 1 order by est_delivery asc;

CREATE TABLE orders(order_id integer, seller_id integer, order_name, user_id integer, source_address, dest_address,start_ware, end_ware, est_delivery datetime, "order_startdate datetime", primary key(order_id),foreign key(user_id) references user(id));

insert into orders (order_id, seller_id, order_name, user_id, est_delivery) values (1,1,"HP",1,"2018-08-20"




select order_name from orders where est_delivery = "2018-08-25"  order by est_delivery asc;