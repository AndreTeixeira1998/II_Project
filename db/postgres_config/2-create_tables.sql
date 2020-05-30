SET search_path TO FACTORY;

CREATE TYPE order_state AS ENUM ('processed','active', 'suspended', 'pending');
CREATE TYPE piece_state AS ENUM ('pending', 'stored', 'assemblying', 'dispatched');

CREATE TABLE orders(
    order_id INTEGER PRIMARY KEY,
    received_time TIMESTAMPTZ DEFAULT (NOW()),
	start_time TIMESTAMPTZ,
	end_time TIMESTAMPTZ,
	maxdelay INTEGER DEFAULT 0,-- é o prazo relativo... se calhar era melhor mudar o nome
	curr_state ORDER_STATE DEFAULT 'pending'
);

CREATE TABLE transform_orders(
	before_type INTEGER NOT NULL,
	after_type INTEGER NOT NULL,
	batch_size INTEGER DEFAULT (1),
	produced INTEGER DEFAULT (0) CHECK (produced <= batch_size),
	on_factory INTEGER DEFAULT (0) CHECK (on_factory <= batch_size),
	pending INTEGER DEFAULT(1) CHECK (pending <= batch_size),
	PRIMARY KEY (order_id)
)INHERITS (orders);

CREATE TABLE unload_orders(
	curr_type INTEGER NOT NULL,
	destination INTEGER NOT NULL, -- DUNNO q tipo por.. fica integer por agr
	batch_size INTEGER DEFAULT (1),
	unloaded INTEGER DEFAULT (0) CHECK (unloaded <= batch_size),
	PRIMARY KEY (order_id)
)INHERITS (orders);

CREATE TABLE stock_orders(
)INHERITS (orders);


CREATE TABLE pieces (
	piece_id serial PRIMARY KEY,
	piece_type INTEGER NOT NULL,
	piece_state PIECE_STATE DEFAULT 'pending',
	associated_order INTEGER
);

CREATE TABLE stored_pieces (
	piece_type INTEGER NOT NULL,
	amount INTEGER DEFAULT(54) CHECK (amount >= 0)
);

CREATE TABLE machines(
	machine_id  SERIAL PRIMARY KEY,
	machine_type CHAR(1),
	transformation_cell INTEGER,
	total_time INTEGER DEFAULT (0),
	P1 INTEGER DEFAULT (0),
	P2 INTEGER DEFAULT (0),
	P3 INTEGER DEFAULT (0),
	P4 INTEGER DEFAULT (0),
	P5 INTEGER DEFAULT (0),
	P6 INTEGER DEFAULT (0),
	P7 INTEGER DEFAULT (0),
	P8 INTEGER DEFAULT (0),
	P9 INTEGER DEFAULT (0),
	total INTEGER DEFAULT (0),
	UNIQUE (machine_type, transformation_cell)
);

CREATE TABLE transformations(
	transform_id SERIAL PRIMARY KEY,
	machine INTEGER REFERENCES machines(machine_id) NOT NULL,
	tool INTEGER NOT NULL,
	initial_type INTEGER NOT NULL,
	final_type INTEGER NOT NULL,
	duration INTEGER NOT NULL,
	UNIQUE (machine, tool)
);

CREATE TABLE operations(
	op_id SERIAL PRIMARY KEY,
	piece_id INTEGER REFERENCES pieces(piece_id) NOT NULL,
	order_id INTEGER REFERENCES orders(order_id) NOT NULL
);
CREATE TABLE transform_operations(
	transform_id INTEGER REFERENCES transformations(transform_id)
) INHERITS (operations);


CREATE TABLE unloading_zones(
	area_id INTEGER PRIMARY KEY,
	P1 INTEGER DEFAULT (0),
	P2 INTEGER DEFAULT (0),
	P3 INTEGER DEFAULT (0),
	P4 INTEGER DEFAULT (0),
	P5 INTEGER DEFAULT (0),
	P6 INTEGER DEFAULT (0),
	P7 INTEGER DEFAULT (0),
	P8 INTEGER DEFAULT (0),
	P9 INTEGER DEFAULT (0)
);

CREATE TABLE unload_operations(
	unloading_area INTEGER REFERENCES unloading_zones(area_id),
	-- uma peça nao pode ser descarregada duas vezes
	CONSTRAINT byebye_piece UNIQUE (piece_id)
) INHERITS (operations);

