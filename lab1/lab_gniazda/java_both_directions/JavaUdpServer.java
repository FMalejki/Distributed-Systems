package java_both_directions;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;

public class JavaUdpServer {
    public static void main(String args[]) {
        System.out.println("JAVA UDP SERVER");
        DatagramSocket socket = null;
        int portNumber = 9008;

        try {
            socket = new DatagramSocket(portNumber);
            byte[] receiveBuffer = new byte[1024];

            while (true) {
                Arrays.fill(receiveBuffer, (byte) 0);
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                
                socket.receive(receivePacket);
                String msg = new String(receivePacket.getData(), 0, receivePacket.getLength());
                System.out.println("Received msg: " + msg);

                InetAddress senderAddress = receivePacket.getAddress();
                int senderPort = receivePacket.getPort();
                System.out.println("Sender: " + senderAddress + ":" + senderPort);

                byte[] sendBuffer = ("Echo from Server: " + msg).getBytes();
                DatagramPacket sendPacket = new DatagramPacket(
                        sendBuffer, sendBuffer.length, senderAddress, senderPort
                );
                socket.send(sendPacket);
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (socket != null) socket.close();
        }
    }
}