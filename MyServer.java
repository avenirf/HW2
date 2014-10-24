//Server Side Program.

import java.net.*;
import java.io.*;

class MyServer
{
ServerSocket ss;
Socket clientsocket;
BufferedReader fromclient;
InputStreamReader isr;
PrintWriter toclient;

public MyServer()
	{
	String str = new String("hello");
	try
		{

		// Create ServerSocket object.
		ss = new ServerSocket(1234);
		System.out.println("Server Started...");
		while(true)
		{
			System.out.println("Waiting for the client...");
			clientsocket = ss.accept();
while(true)
{
		System.out.println("Waiting for the request...");

		// accept the client request.
		//clientsocket = ss.accept();

		System.out.println("Got a client");
		System.out.println("Client Address "+ clientsocket.getInetAddress().toString());
		isr = new InputStreamReader(clientsocket.getInputStream());
		fromclient = new BufferedReader(isr);

		toclient = new PrintWriter(clientsocket.getOutputStream());

		str = fromclient.readLine();
		System.out.println(str);

		toclient.println("Server : Your Message Recieved ");
		System.out.println("Response sent to the client " + toclient.checkError());
if(str.equals("bye"))
	{
	fromclient.close();
	toclient.close();
	clientsocket.close();
	break;
	}
}
		}
		//fromclient.close();
		//toclient.close();
		//clientsocket.close();
		}
	catch(Exception ex)
		{
		System.out.println("Error in the code : " + ex.toString());
		}
	}

public static void main(String arg[])
	{
	MyServer serverobj = new MyServer();
	}
}
