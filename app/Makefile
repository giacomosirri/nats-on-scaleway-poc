CC = gcc
CFLAGS = -Wall -Wpedantic -I/usr/local/include/nats -L/usr/local/lib/ -lnats -ljansson -lcurl -lglib-2.0 

SOURCE_PATH = ./src
BIN_PATH = ./bin

SOURCE = $(SOURCE_PATH)/nats_client.c
OBJ = $(BIN_PATH)/nats_client.o
PROGRAM = $(BIN_PATH)/nats_client

default: $(PROGRAM)

$(OBJ): $(SOURCE)
	$(CC) -o2 -c $(SOURCE) $(CFLAGS) -o $(OBJ) `pkg-config --cflags glib-2.0`

$(PROGRAM): $(OBJ)
	$(CC) $(OBJ) $(CFLAGS) -o $(PROGRAM)

clean:
	rm -f $(OBJ) $(PROGRAM)