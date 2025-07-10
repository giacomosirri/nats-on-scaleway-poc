extern int BUFFER_SIZE; // Size of the buffer for the response payload

size_t write_callback(void *payload_chunk, size_t size, size_t nmemb, void *user_buffer);

int writeCredentialsToFile(char *credentials, char *filename, int size);

int getPlainTextCredentials(char *decoded_credentials_string);

int nats_Cleanup(natsConnection *conn, natsOptions *opts, natsStatus s);

char* build_nats_subject(const char* vehicle_id, const char* topic);

double getRandomValue(double min, double max) ;