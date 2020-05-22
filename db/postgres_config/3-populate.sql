SET search_path TO FACTORY;

INSERT into transform_orders (order_id, before_type, after_type, batch_size) VALUES (1, 1, 2, 50);
INSERT into transform_orders (order_id, before_type, after_type, batch_size) VALUES (2, 4, 1, 0);
INSERT into transform_orders (order_id, before_type, after_type, batch_size, curr_state) VALUES (3, 1, 1, 50, 'active');

INSERT into unload_orders (order_id, curr_type, destination, batch_size) VALUES (4, 1, 1, 50);

INSERT into stock_orders (order_id, received_time) VALUES (6, '2016-06-22 19:10:25-07');


do $$ --Insere as maquinas de cada tipo na base de dados, default 0 para os outros tipos de dado
	begin
		for i in 1..3 loop
			insert into machines (machine_type, transformation_cell) values('A', i);
			insert into machines (machine_type, transformation_cell) values('B', i);
			insert into machines (machine_type, transformation_cell) values('C', i);
		end loop;
	end;
$$;

do $$ --Insere as peças inicias do armazem
	begin
		for ptype in 1..9 loop
			for i in 1..54 loop
				INSERT INTO pieces (piece_type,piece_state) VALUES (ptype,'stored');
			end loop;
		end loop;
	end;
$$;

do $$ --Insere as peças inicias do armazem
	begin
		for ptype in 1..9 loop
			INSERT INTO stored_pieces (piece_type) VALUES (ptype);
		end loop;
	end;
$$;

do $$ --Insere as zonas de descarga com default de descarga por peça 0
	begin
		for i in 1..3 loop
			INSERT INTO unloading_zones (area_id) VALUES (i);
		end loop;
	end;
$$;

INSERT INTO transformations (machine, tool, initial_type, final_type, duration)
	VALUES(
		(SELECT machine_id FROM machines WHERE machine_type = 'A' and transformation_cell = 1),
		1,
		1,
		2,
		15
	);

INSERT INTO transform_operations (piece_id, order_id , transform_id)
	VALUES(
		1,
		5,
		(SELECT transform_id FROM transformations
			 INNER JOIN machines ON transformations.machine = machines.machine_id
				WHERE machines.machine_type = 'A' AND transformations.tool = 1)
	);
