INSERT into factory.orders DEFAULT VALUES;
INSERT into factory.orders DEFAULT VALUES;
INSERT into factory.orders DEFAULT VALUES;
INSERT into factory.orders DEFAULT VALUES;

INSERT into factory.transform_orders (before_type, after_type, batch_size) VALUES ('P1', 'P4', 50);
INSERT into factory.transform_orders (before_type, after_type, batch_size) VALUES ('P3', 'P4', 25);
INSERT into factory.transform_orders (before_type, after_type, batch_size, curr_state) VALUES ('P1', 'P4', 50, 'active');

do $$
	begin
		for i in 1..10 loop
			insert into factory.pieces(piece_type) values('P1');
			insert into factory.pieces(piece_type) values('P3');
			insert into factory.pieces(piece_type) values('P2');
			insert into factory.pieces(piece_type) values('P5');
			insert into factory.pieces(piece_type) values('P9');
		end loop;
	end;
$$;