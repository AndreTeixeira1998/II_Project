SET search_path TO FACTORY;

CREATE TABLE orders(
    order_id SERIAL PRIMARY KEY,
    received_time TIMESTAMPTZ DEFAULT (NOW()),
	start_time TIMESTAMPTZ,
	end_time TIMESTAMPTZ,
	curr_state ORDER_STATE DEFAULT 'pending'
);

CREATE TABLE transform_orders(
	before_type PIECE_TYPE NOT NULL,
	after_type PIECE_TYPE NOT NULL,
	batch_size INTEGER DEFAULT (1),
	produced INTEGER DEFAULT (0) CHECK (produced <= batch_size)
)INHERITS (orders);

CREATE TABLE unload_orders(
	curr_type PIECE_TYPE NOT NULL,
	destination INTEGER NOT NULL, -- DUNNO q tipo por.. fica integer por agr
	batch_size INTEGER DEFAULT (1),
	unloaded INTEGER DEFAULT (0) CHECK (unloaded <= batch_size)
)INHERITS (orders);

CREATE TABLE stock_orders(
)INHERITS (orders);


CREATE TABLE pieces (
	piece_id serial PRIMARY KEY,
	piece_type PIECE_TYPE NOT NULL,
	associated_order INTEGER REFERENCES orders(order_id)
);