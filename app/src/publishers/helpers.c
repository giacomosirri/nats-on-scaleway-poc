#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <nats/nats.h>
#include <curl/curl.h>
#include <jansson.h>
#include <glib.h>

int BUFFER_SIZE = 4096; // Size of the buffer for the response payload

// Buffer structure to hold the JSON response payload
struct Buffer
{
    char *data;
    size_t size;
};

size_t write_callback(void *payload_chunk, size_t size, size_t nmemb, void *user_buffer)
{
    struct Buffer *buffer = (struct Buffer *) user_buffer;
    // 'size' represents the size of each element, 'nmemb' is the number of elements.
    size_t total_size = size * nmemb;
    // Prevent buffer overflow.
    if (total_size + buffer->size > BUFFER_SIZE - 1) {
        fprintf(stderr, "Buffer overflow prevented: %zu bytes exceeds buffer size of %d\n", total_size, BUFFER_SIZE);
        return 0;
    }
    // Copy in-place this chunk of the payload to the memory buffer.
    memcpy(&(buffer->data[buffer->size]), payload_chunk, total_size);
    // Move the pointer forward by the size of the chunk.
    buffer->size += total_size;
    // Ensure null-termination.
    buffer->data[buffer->size] = '\0';
    // Return the total size of the data written.
    return total_size;
}

int write_credentials_to_file(char *credentials, char *filename, int size)
{
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        return 0;
    } else {
        fwrite(credentials, 1, size, file);
        fclose(file);
        return 1;
    }
}

int get_plain_text_credentials(char *decoded_credentials_string)
{
    gsize credentials_len = 0; // Length of the decoded credentials
    CURL *curl;
    CURLcode res;
    struct Buffer *buffer;
    char *region = "fr-par";
    char *project_id = "d43489e8-6103-4cc8-823b-7235300e81ec";
    char *secret_name = "nats-credentials";
    char *secret_path = "/";
    char *api_endpoint = "https://api.scaleway.com/secret-manager/v1beta1/regions/%s/secrets-by-path/versions/latest/access?project_id=%s&secret_name=%s&secret_path=%s";
    char *scaleway_token = getenv("SCW_ACCESS_KEY");

    if (scaleway_token == NULL) {
        fprintf(stderr, "Cannot retrieve Scaleway access key from environment variables.\n");
        return 0;
    }

    // Allocate memory for the buffer.
    buffer = malloc(sizeof(struct Buffer));
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate memory for buffer.\n");
        return 0;
    }
    buffer->data = malloc(BUFFER_SIZE); // Allocate BUFFER_SIZE KB for the response data
    if (buffer->data == NULL) {
        fprintf(stderr, "Failed to allocate memory for response data.\n");
        free(buffer);
        return 0;
    }
    buffer->size = 0; // Initialize size to 0

    // Create the API endpoint URL string.
    char url[512];
    snprintf(url, sizeof(url), api_endpoint, region, project_id, secret_name, secret_path);

    // Construct the authentication header.
    char auth_header[256];
    snprintf(auth_header, sizeof(auth_header), "X-Auth-Token: %s", scaleway_token);

    // Create the struct to contain the headers of the CURL request.
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, auth_header);

    // Initialize the CURL library.
    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();

    if (curl) {
        // Set CURL options for the request.
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, buffer); // Set the fourth argument of the callback function to the buffer

        // Perform the CURL request.
        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "Request failed: %s\n", curl_easy_strerror(res));
        } else {
            // Parse the returned JSON payload using jansson.
            json_error_t error;
            json_t *root = json_loads(buffer->data, 0, &error);
            if (!root) {
                fprintf(stderr, "JSON parse error: %s\n", error.text);
            } else {
                // Parse the JSON response to extract the secret.
                json_t *secret_data = json_object_get(root, "data");
                if (!json_is_string(secret_data)) {
                    fprintf(stderr, "Data field not found or not a string\n");
                } else {
                    guchar *decoded_credentials = g_base64_decode(json_string_value(secret_data), &credentials_len);
                    if (credentials_len > BUFFER_SIZE) {
                        fprintf(stderr, "Decoded credentials length exceeds buffer size.\n");
                        return 0;
                    } else {
                        // Cast the decoded credential value to an array of chars.
                        for (int i=0; i<(int)credentials_len; i++) {
                            decoded_credentials_string[i] = decoded_credentials[i];
                        }
                        decoded_credentials_string[credentials_len] = '\0'; // Null-terminate the string
                    }
                }
                json_decref(root); // Free memory
            }
        }
        curl_easy_cleanup(curl);
    }

    // Cleanup CURL resources.
    curl_slist_free_all(headers);
    curl_global_cleanup();

    free(buffer->data);
    free(buffer);

    // Return the length of the decoded credentials.
    return (int)credentials_len;
}

int nats_Cleanup(natsConnection *conn, natsOptions *opts, natsStatus s)
{
    printf("NATS status: %s\n", natsStatus_GetText(s));
    natsConnection_Destroy(conn);
    natsOptions_Destroy(opts);
    nats_Close();
    return (s == NATS_OK ? 0 : 1);
}

char* build_nats_subject(const char* vehicle_id, const char* topic)
{
    const char* prefix = "vehicle";
    const char* dot = ".";

    size_t len = strlen(prefix) + strlen(vehicle_id) + strlen(dot) + strlen(topic) + 1; // +1 for null terminator
    char* subject = malloc(len);
    if (!subject) return NULL; // malloc failed

    // Concatenate the strings to form the subject.
    strcpy(subject, prefix);
    strcat(subject, dot);
    strcat(subject, vehicle_id);
    strcat(subject, dot);
    strcat(subject, topic);

    return subject;
}

double get_random_value(double min, double max) 
{
    double scale = rand() / (double) RAND_MAX; // Scale in [0, 1)
    double value = min + scale * (max - min);
    return value;
}
