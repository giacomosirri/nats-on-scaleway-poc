CC = gcc
CFLAGS = -o2 -Wall -Wpedantic -I/usr/local/include/nats -I./src/publishers
LDFLAGS = -L/usr/local/lib -L$(BIN_PATH)
LDLIBS = -lnats -ljansson -lcurl -lglib-2.0

SOURCE_PATH = ./src/publishers
BIN_PATH = ./bin

SOURCE = $(SOURCE_PATH)/nats_client.c
SOURCE_HELPERS_LIB = $(SOURCE_PATH)/helpers.c

OBJ = $(BIN_PATH)/nats_client.o
OBJ_HELPERS_LIB = $(BIN_PATH)/helpers.o

HELPERS_SHARED_LIB = $(BIN_PATH)/libhelpers.so
PROGRAM = $(BIN_PATH)/nats_client



default: $(PROGRAM)

$(OBJ_HELPERS_LIB): $(SOURCE_HELPERS_LIB)
	$(CC) $(CFLAGS) `pkg-config --cflags-only-I glib-2.0` -fPIC -c $(SOURCE_HELPERS_LIB) -o $(OBJ_HELPERS_LIB) 

$(OBJ): $(SOURCE)
	$(CC) $(CFLAGS) `pkg-config --cflags-only-I glib-2.0` -c $(SOURCE) -o $(OBJ)

$(HELPERS_SHARED_LIB): $(OBJ_HELPERS_LIB)
	$(CC) -shared $(OBJ_HELPERS_LIB) $(LDFLAGS) $(LDLIBS) -o $(HELPERS_SHARED_LIB)

$(PROGRAM): $(OBJ) $(HELPERS_SHARED_LIB)
	$(CC) $(OBJ) $(LDFLAGS) $(LDLIBS) -lhelpers -Wl,-rpath=$(BIN_PATH) -o $(PROGRAM)

.PHONY: clean

clean:
	rm -f $(OBJ) $(PROGRAM)