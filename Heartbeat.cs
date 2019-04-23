using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.Serialization.Json;
using System.Runtime.Serialization;

namespace IoTRouter
{
    [DataContract]
    public class HeartBeat
    {
        [DataMember]
        public string StoreId;

        [DataMember]
        public bool IsActive;

        public HeartBeat(string Id, bool active)
        {
            StoreId = Id;
            IsActive = active;
        }
    }
}
