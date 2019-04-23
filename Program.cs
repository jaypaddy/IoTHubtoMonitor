using System;
using System.Globalization;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Runtime.Serialization.Json;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace IoTRouter
{
    class Program
    {
        static void Main(string[] args)
        {
            //Generate IoT Hub Token
            string iotHub_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=";
            //append device name
            string StoreId = "S1001";
            string iotHub_uri = "xxxxxxx.azure-devices.net/devices/" + StoreId + "/messages/events?api-version=2018-06-30";
            string iotHub_policy_name = "xxxxxxxxx";
            string iotHub_SAS_Token = GenerateSasToken(iotHub_uri, iotHub_key, iotHub_policy_name);
            string hbJSON = GetHeartBeat(StoreId);

            PostToIoTHub("https://"+iotHub_uri, hbJSON, iotHub_SAS_Token).Wait();

        }

        public static string GenerateSasToken(string resourceUri, string key, string policyName, int expiryInSeconds = 3600)
        {
            TimeSpan fromEpochStart = DateTime.UtcNow - new DateTime(1970, 1, 1);
            string expiry = Convert.ToString((int)fromEpochStart.TotalSeconds + expiryInSeconds);
            string stringToSign = WebUtility.UrlEncode(resourceUri) + "\n" + expiry;

            HMACSHA256 hmac = new HMACSHA256(Convert.FromBase64String(key));
            string signature = Convert.ToBase64String(hmac.ComputeHash(Encoding.UTF8.GetBytes(stringToSign)));

            string token = String.Format(CultureInfo.InvariantCulture, "sr={0}&sig={1}&se={2}", WebUtility.UrlEncode(resourceUri), WebUtility.UrlEncode(signature), expiry);

            if (!String.IsNullOrEmpty(policyName))
            {
                token += "&skn=" + policyName;
            }

            return token;
        }

        public static string GetHeartBeat(string StoreId)
        {
            HeartBeat hb = new HeartBeat(StoreId, true);
            DataContractJsonSerializer js = new DataContractJsonSerializer(typeof(HeartBeat));
            MemoryStream ms = new MemoryStream();
            js.WriteObject(ms, hb);
            ms.Position = 0;
            StreamReader sr = new StreamReader(ms);
            string hbJSON = sr.ReadToEnd();
            sr.Close();
            ms.Close();

            return hbJSON;
        }

        public static async Task<string> PostToIoTHub(string uri, string data, string SASToken)
        {
            try
            {
                var httpClient = new System.Net.Http.HttpClient();
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("SharedAccessSignature",SASToken);
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                var payload = new StringContent(data, Encoding.UTF8, "application/json");
                HttpResponseMessage response = await httpClient.PostAsync(uri, payload);
                string retMsg = await response.Content.ReadAsStringAsync();
                if (response.StatusCode == HttpStatusCode.OK)
                {
                    Console.WriteLine(retMsg);
                    return retMsg;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                return ex.ToString();
            }
            return "";
        }
    }

}
