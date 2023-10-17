import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class FlightBookingApp {

    public static void main(String[] args) {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

        System.out.println("Welcome to the Flight Booking App!");

        try {
            System.out.print("Enter your name: ");
            String passengerName = reader.readLine();

            System.out.print("Enter departure city: ");
            String departureCity = reader.readLine();

            System.out.print("Enter destination city: ");
            String destinationCity = reader.readLine();

            System.out.print("Enter departure date (YYYY-MM-DD): ");
            String departureDate = reader.readLine();

            System.out.print("Enter number of passengers: ");
            int numberOfPassengers = Integer.parseInt(reader.readLine());

            System.out.println("\nBooking Summary:");
            System.out.println("Passenger Name: " + passengerName);
            System.out.println("Departure City: " + departureCity);
            System.out.println("Destination City: " + destinationCity);
            System.out.println("Departure Date: " + departureDate);
            System.out.println("Number of Passengers: " + numberOfPassengers);
            System.out.println("Booking confirmed. Have a safe flight!");
        } catch (IOException | NumberFormatException e) {
            System.out.println("Error reading input. Exiting.");
        }
    }
}
