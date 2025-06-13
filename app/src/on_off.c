#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <nats/nats.h>
#include <curl/curl.h>
#include <jansson.h>
#include <glib.h>

int BUFFER_SIZE = 4096; // Size of the buffer for response data

// Buffer structure to hold JSON response data
struct Buffer {
    char *data;
    size_t size;
};

static size_t write_callback(void *ptr, size_t size, size_t nmemb, void *userdata) {
    // Cast userdata to Buffer type.
    struct Buffer *buffer = (struct Buffer *)userdata;
    // 'size' represents the size of each element, 'nmemb' is the number of elements.
    size_t total_size = size * nmemb;
    if (total_size + buffer->size > BUFFER_SIZE - 1) {
      fprintf(stderr, "Buffer overflow prevented: %zu bytes exceeds buffer size of %d\n", total_size, BUFFER_SIZE);
      return 0; // Prevent buffer overflow
    }
    // Copy in-place the content to the buffer.
    memcpy(&(buffer->data[buffer->size]), ptr, total_size);
    // Move the pointer forward by the size of the data written.
    buffer->size += total_size;
    // Ensure null-termination.
    buffer->data[buffer->size] = '\0';
    return total_size;
}

char* getPlainTextCredentials()
{
    CURL *curl;
    CURLcode res;
    struct Buffer *buffer;
    const char *region = "fr-par";
    const char *project_id = "d43489e8-6103-4cc8-823b-7235300e81ec";
    const char *secret_name = "nats-credentials";
    const char *secret_path = "/";
    // Scaleway API Access Key
    const char *token = "6a336881-1ce2-4ba9-a760-917fc8b3f886"; // Read from env
    char *api_endpoint = "https://api.scaleway.com/secret-manager/v1beta1/regions/%s/secrets-by-path/versions/latest/access?project_id=%s&secret_name=%s&secret_path=%s";
    char *decoded_secret = NULL;

    // Allocate memory for the buffer
    buffer = malloc(sizeof(struct Buffer));
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate memory for buffer.\n");
        return NULL;
    }
    buffer->data = malloc(BUFFER_SIZE); // Allocate BUFFER_SIZE KB for the response data
    if (buffer->data == NULL) {
        fprintf(stderr, "Failed to allocate memory for response data.\n");
        free(buffer);
        return NULL;
    }
    buffer->size = 0; // Initialize size to 0

    char url[512];
    snprintf(url, sizeof(url), api_endpoint, region, project_id, secret_name, secret_path);

    // Construct the authentication header.
    char auth_header[256];
    snprintf(auth_header, sizeof(auth_header), "X-Auth-Token: %s", token);

    // Create the struct to contain the headers of the CURL request.
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, auth_header);

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();

    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, buffer); // Write to stdout

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "Request failed: %s\n", curl_easy_strerror(res));
        } else {
            // Parse JSON using jansson
            json_error_t error;
            json_t *root = json_loads(buffer->data, 0, &error);
            if (!root) {
                fprintf(stderr, "JSON parse error: %s\n", error.text);
            } else {
                // Parse the JSON response to extract the secret.
                json_t *secret_data = json_object_get(root, "data");
                if (json_is_string(secret_data)) {
                    gsize out_len;
                    // Set the return value of this function.
                    char *decoded_credentials = (char *)(g_base64_decode(json_string_value(secret_data), &out_len));
                } else {
                    printf("Data field not found or not a string\n");
                }
                json_decref(root); // Free memory
            }
        }
        curl_easy_cleanup(curl);
    }

    curl_slist_free_all(headers);
    curl_global_cleanup();

    return decoded_credentials;
}

int nats_Cleanup(natsConnection *conn, natsOptions *opts, natsStatus s)
{
    printf("%s\n", natsStatus_GetText(s));
    natsConnection_Destroy(conn);
    natsOptions_Destroy(opts);
    nats_Close();
    return (s == NATS_OK ? 0 : 1);
}

int main(int argc, char **argv)
{
    char filename[] = "nats-credentials.txt";
    char natsServerUrl[] = "nats://nats.mnq.fr-par.scaleway.com:4222";

    natsConnection *conn = NULL;
    natsStatus s;
    natsOptions *opts = NULL;
    
    // Initialize NATS options structure.
    s = natsOptions_Create(&opts);
    if (s != NATS_OK) {
      nats_Cleanup(conn, opts, s);
    }
    
    // Set server URL.
    s = natsOptions_SetURL(opts, natsServerUrl);
    if (s != NATS_OK) {
      nats_Cleanup(conn, opts, s);
    }

    // Get NATS credentials from Scaleway Secret Manager.
    char *plainTextCredentials = getPlainTextCredentials();
    writeCredentialsToFile(plainTextCredentials, filename);

    // Set credentials file path.
    s = natsOptions_SetUserCredentialsFromFiles(opts, filename, NULL);
    if (s != NATS_OK) {
      nats_Cleanup(conn, opts, s);
    }

    // Connect to the NATS server.
    s = natsConnection_Connect(&conn, opts);
    if (s != NATS_OK) {
      nats_Cleanup(conn, opts, s);
    }

    // Publish a message to subject "foo".
    s = natsConnection_PublishString(conn, "foo", "Hello from C!");
    if (s != NATS_OK) {
        nats_Cleanup(conn, opts, s);
    }

    printf("Message published to subject 'foo'\n");
    // Final cleanup.
    nats_Cleanup(conn, opts, s);
}
