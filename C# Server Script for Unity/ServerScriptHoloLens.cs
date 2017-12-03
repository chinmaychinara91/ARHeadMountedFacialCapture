// This is the server script that receives the data transmitted
// by the client, decodes it and displays it in a GUI either in Unity
// or HoloLens
// code encapsulated in directive "UNITY_EDITOR" will run only in Unity
// code encapsulated in directive "!UNITY_EDITOR && UNITY_UWP" will run only on UWP platforms (here HoloLens)
// Author: Chinmay Chinara and Aakash Shanbhag
//////////////////////////////////////////////////////////////////////////////////////////////////////////////

using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;

#if UNITY_EDITOR
    // using Raw TCP/IP sockets
    using System.Net;
    using System.Net.Sockets;
#endif

#if !UNITY_EDITOR && UNITY_UWP
    // using Windows.Networking Raw TCP/IP sockets for UWP as .Net sockets
    // are not supported in UWP applications
    using System.Linq;
    using System.Runtime.InteropServices.WindowsRuntime;
    using Windows.Networking;
    using Windows.Networking.Connectivity;
    using Windows.Networking.Sockets;
    using System.Threading.Tasks;
    using Windows.Storage.Streams;
#endif

public class ServerScriptHoloLens : MonoBehaviour
{
#if UNITY_EDITOR
    public int val = 0;

    Texture2D thisTexture1;
    Texture2D thisTexture2;
    Texture2D thisTexture3;

    private GameObject g1;
    private GameObject g2;
    private GameObject g3;

    private GameObject ser2;
    private GameObject ser4;
    private GameObject ser6;

    IPEndPoint iep2 = new IPEndPoint(IPAddress.Parse("10.1.6.39"), 5001);
    IPEndPoint iep4 = new IPEndPoint(IPAddress.Parse("10.1.6.39"), 5003);
    IPEndPoint iep6 = new IPEndPoint(IPAddress.Parse("10.1.6.39"), 5005);

    Socket server2 = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
    Socket server4 = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
    Socket server6 = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

    Socket client2 = null;
    Socket client4 = null;
    Socket client6 = null;

    void Start ()
    {
        ser2 = this.transform.Find("Ser2").gameObject;
        ser4 = this.transform.Find("Ser4").gameObject;
        ser6 = this.transform.Find("Ser6").gameObject;

        server2.Bind(iep2);
        server4.Bind(iep4);
        server6.Bind(iep6);

        server2.Listen(10);
        server4.Listen(10);
        server6.Listen(10);

        Debug.Log("Waiting for connection...\n");
        client2 = server2.Accept();
        client4 = server4.Accept();
        client6 = server6.Accept();

        Debug.Log("Connected...\n");
        if (client2.Connected)
            ser2.GetComponent<Text>().text = "Connected2";
        if (client4.Connected)
            ser4.GetComponent<Text>().text = "Connected4";
        if (client6.Connected)
            ser6.GetComponent<Text>().text = "Connected6";

        g1 = this.transform.Find("RawImage_LeftEye").gameObject;
        g2 = this.transform.Find("RawImage_RightEye").gameObject;
        g3 = this.transform.Find("RawImage_Mouth").gameObject;
    }

    byte[] buffer2 = new byte[10000000];
    byte[] buffer4 = new byte[10000000];
    byte[] buffer6 = new byte[10000000];

    // Update is called once per frame
    void Update ()
    {
        int buffer2_len = client2.Receive(buffer2);
        int buffer4_len = client4.Receive(buffer4);
        int buffer6_len = client6.Receive(buffer6);

        thisTexture1 = new Texture2D(640, 480);
        thisTexture2 = new Texture2D(640, 480);
        thisTexture3 = new Texture2D(640, 480);
     
        // This check is done to enure that correct JPEG frames are received
        // Ideally for a correct jpeg frame, the first four bytes should be FF D8 FF E0
        // and the last 2 byte should be FF D9
        if (buffer2[0] == 255  && buffer2[1] == 216 && buffer2[2] == 255 && buffer2[3] == 224 && buffer2[buffer2_len - 2] == 255 && buffer2[buffer2_len - 1] == 217)
        {
            thisTexture1.LoadImage(buffer2);
            g1.GetComponent<RawImage>().texture = thisTexture1;
        }          
        else
        {
           Debug.Log("buffer2[0]: " + buffer2[0].ToString() + " "
                + buffer2[1].ToString() + " "
                + buffer2[2].ToString() + " "
                + buffer2[3].ToString() + " "
                + buffer2[buffer2_len - 2].ToString() + " "
                + buffer2[buffer2_len - 1].ToString());
        }

        // This check is done to enure that correct JPEG frames are received
        // Ideally for a correct jpeg frame, the first four bytes should be FF D8 FF E0
        // and the last 2 byte should be FF D9
        if (buffer4[0] == 255 && buffer4[1] == 216 && buffer4[2] == 255 && buffer4[3] == 224 && buffer4[buffer4_len - 2] == 255 && buffer4[buffer4_len - 1] == 217)
        {
            thisTexture2.LoadImage(buffer4);
            g2.GetComponent<RawImage>().texture = thisTexture2;
        }
        else
        {
            Debug.Log("buffer4[0]: " + buffer4[0].ToString() + " "
                + buffer4[1].ToString() + " "
                + buffer4[2].ToString() + " "
                + buffer4[3].ToString() + " "
                + buffer4[buffer2_len - 2].ToString() + " "
                + buffer4[buffer2_len - 1].ToString());
        }

        // This check is done to enure that correct JPEG frames are received
        // Ideally for a correct jpeg frame, the first four bytes should be FF D8 FF E0
        // and the last 2 byte should be FF D9
        if (buffer6[0] == 255 && buffer6[1] == 216 && buffer6[2] == 255 && buffer6[3] == 224 && buffer6[buffer6_len - 2] == 255 && buffer6[buffer6_len - 1] == 217)
        {
            thisTexture3.LoadImage(buffer6);
            g3.GetComponent<RawImage>().texture = thisTexture3;
        }
        else
        {
            Debug.Log("buffer6[0]: " + buffer6[0].ToString() + " "
                + buffer6[1].ToString() + " "
                + buffer6[2].ToString() + " "
                + buffer6[3].ToString() + " "
                + buffer6[buffer2_len - 2].ToString() + " "
                + buffer6[buffer2_len - 1].ToString());
        }

        System.Threading.Thread.Sleep(val);
        //transform.Translate(0, 0, Time.deltaTime * 1);
    }
#endif

#if !UNITY_EDITOR && UNITY_UWP
    public int val = 0;

    Texture2D thisTexture1;
    Texture2D thisTexture2;
    Texture2D thisTexture3;

    private GameObject g1;
    private GameObject g2;
    private GameObject g3;

    private GameObject ser2;
    private GameObject ser4;
    private GameObject ser6;

    StreamSocketListener socket2 = null;
    StreamSocketListener socket4 = null;
    StreamSocketListener socket6 = null;

    //Create the StreamSocket and establish a connection to the echo server.
    HostName serverHost = new HostName("10.1.7.130");
    int serverPort2 = 5001;
    int serverPort4 = 5003;
    int serverPort6 = 5005;

    byte[] buffer2 = new byte[1000000];
    byte[] buffer4 = new byte[1000000];
    byte[] buffer6 = new byte[1000000];

    string server2_text = "Not Connected 2";
    string server4_text = "Not Connected 4";
    string server6_text = "Not Connected 6";

    int cnt2 = 0;
    int cnt4 = 0;
    int cnt6 = 0;

    void Start()
    {
        g1 = this.transform.Find("RawImage_LeftEye").gameObject;
        g2 = this.transform.Find("RawImage_RightEye").gameObject;
        g3 = this.transform.Find("RawImage_Mouth").gameObject;

        ser2 = this.transform.Find("Ser2").gameObject;
        ser4 = this.transform.Find("Ser4").gameObject;
        ser6 = this.transform.Find("Ser6").gameObject;

        ser2.GetComponent<Text>().text = server2_text;
        ser6.GetComponent<Text>().text = server4_text;
        ser4.GetComponent<Text>().text = server6_text;

        ConnectMe();
    }

    void Update()
    {
        ser2.GetComponent<Text>().text = server2_text;
        ser6.GetComponent<Text>().text = server4_text;
        ser4.GetComponent<Text>().text = server6_text;

        if(server2_text == "here_here")
        {
            thisTexture1 = new Texture2D(640, 480);
            thisTexture1.LoadImage(buffer2);
            g1.GetComponent<RawImage>().texture = thisTexture1;
        }

        if (server4_text == "here_here")
        {
            thisTexture2 = new Texture2D(640, 480);
            thisTexture2.LoadImage(buffer4);
            g2.GetComponent<RawImage>().texture = thisTexture2;
        }

        if (server6_text == "here_here")
        {
            thisTexture3 = new Texture2D(640, 480);
            thisTexture3.LoadImage(buffer6);
            g3.GetComponent<RawImage>().texture = thisTexture3;
        }
    }

    private async void ConnectMe()
    {
        try
        {
            socket2 = new StreamSocketListener();
            socket2.ConnectionReceived += Socket2_ConnectionReceived;
            await socket2.BindServiceNameAsync(serverPort2.ToString()); //.AsTask().Wait();

            socket4 = new StreamSocketListener();
            socket4.ConnectionReceived += Socket4_ConnectionReceived;
            await socket4.BindServiceNameAsync(serverPort4.ToString()); //.AsTask().Wait();

            socket6 = new StreamSocketListener();
            socket6.ConnectionReceived += Socket6_ConnectionReceived;
            await socket6.BindServiceNameAsync(serverPort6.ToString()); //.AsTask().Wait();
        }
        catch (Exception e)
        {
            server2_text = "Exception_ConnectMe";
        }
    }

    private void Socket6_ConnectionReceived(StreamSocketListener sender, StreamSocketListenerConnectionReceivedEventArgs args)
    {
        cnt6 += 1;
        server6_text = "Entered";
        try
        {
            server6_text = "here_here";
            using (var reader = new DataReader(args.Socket.InputStream))
            {
                reader.ReadBytes(buffer6);
            }
        }
        catch (Exception e)
        {
            server6_text = "Exception_Ser_" + cnt6.ToString();
        }
    }

    private void Socket4_ConnectionReceived(StreamSocketListener sender, StreamSocketListenerConnectionReceivedEventArgs args)
    {
        cnt4 += 1;
        server4_text = "Entered";
        try
        {
            server4_text = "here_here";
            using (var reader = new DataReader(args.Socket.InputStream))
            {
                reader.ReadBytes(buffer4);
            }
        }
        catch (Exception e)
        {
            server4_text = "Exception_Ser_" + cnt4.ToString();
        }
    }

    private void Socket2_ConnectionReceived(StreamSocketListener sender, StreamSocketListenerConnectionReceivedEventArgs args)
    {
        cnt2 += 1;
        server2_text = "Entered";
        try
        {
            server2_text = "here_here";
            using (var reader = new DataReader(args.Socket.InputStream))
            {
                reader.ReadBytes(buffer2);
            }
        }
        catch (Exception e)
        {
            server2_text = "Exception_Ser_" + cnt2.ToString(); ;
        }
    }
#endif
}
