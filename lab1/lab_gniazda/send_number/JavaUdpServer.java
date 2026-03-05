package send_number;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

public class JavaUdpServer {

    public static void main(String args[]) {
        System.out.println("JAVA UDP SERVER - Number Receiver");
        DatagramSocket socket = null;
        int portNumber = 9008;

        try {
            socket = new DatagramSocket(portNumber);
            byte[] receiveBuffer = new byte[1024];

            while (true) {
                Arrays.fill(receiveBuffer, (byte) 0);
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                
                socket.receive(receivePacket);

                byte[] data = Arrays.copyOfRange(receivePacket.getData(), 0, 4);

                int receivedInt = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN).getInt();
                
                System.out.println("Received number: " + receivedInt);

                int responseInt = receivedInt + 1;

                byte[] sendBuffer = ByteBuffer.allocate(4)
                                              .order(ByteOrder.LITTLE_ENDIAN)
                                              .putInt(responseInt)
                                              .array();

                DatagramPacket sendPacket = new DatagramPacket(
                    sendBuffer, 
                    sendBuffer.length, 
                    receivePacket.getAddress(), 
                    receivePacket.getPort()
                );
                socket.send(sendPacket);
                System.out.println("Sent response: " + responseInt);
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (socket != null) socket.close();
        }
    }
}