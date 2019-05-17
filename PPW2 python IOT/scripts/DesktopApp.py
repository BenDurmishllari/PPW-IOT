# File: DekstopApp.py
# Description: Desktop App PPW2
# Author: Arben Durmishllari, University of Sunderland
# Date: May 2019


# Classes
class DataReading:
	"""
	Class to hold a single data reading, this consists of a given timestamp and given temperature and humidity
	data for this time stamp
	"""
	def __init__(self, timestamp, temp_data, humidity_data):
		"""
		Initialiser - instance variables:
			__timestamp: timestamp for this data reading, as string, property with read-only access
			__temp_data: temperature data for this data reading, as float, property with read-only access
			__humidity_data: humidity data for this data reading, as float, property with read-only access

		:param timestamp: to associate with this data reading instance
		:param temp_data: to associate with this data reading instance
		:param humidity_data: to associate with this data reading instance
		"""
		self.__timestamp = timestamp
		self.__temp_data = temp_data
		self.__humidity_data = humidity_data

	@property
	def timestamp(self):
		return self.__timestamp

	@property
	def temp_data(self):
		return self.__temp_data

	@property
	def humidity_data(self):
		return self.__humidity_data

	def __str__(self):
		"""
		To string method

		:return: string representation of this data reading instance
		"""
		return "Timestamp: {0} {1}c {2}%".format(self.timestamp, self.temp_data, self.humidity_data)


class AccessPeriod:
	"""
	Class to contain a single access period which consists of a number of data readings (timestamp, temperature,
	humidity) associated with a given access period, this class also holds the start and stop date and time of the
	access period, the maximum temperature, average humidity and the approximate length of time in seconds the access
	period lasted
	"""
	def __init__(self, start_date, start_time, staff):
		"""
		Initialiser - instance variables:
			__start_date: start date of this access period, as string, property with read-only access
			__start_time: start time of this access period, as string, property with read-only access
			__stop_date: stop date of this access period, as string, property with read-only access
			__stop_time: stop time of this access period, as string, property with read-only access
			__period_length: approximate number of seconds this access period lasted, as int, property with
			                 read-only access
			__data_readings: list of DataReadings class instances, property with no access
			__temp_max: maximum temperature across all data readings in the data set, as float, property with
						read-only access
			__humidity_average: average humidity across all data readings in the data set, as float, property with
			                    read-only access

		:param start_date: start date of this access period, as string
		:param start_time: start time of this access period, as string
		"""
		self.__start_date = start_date
		self.__start_time = start_time
		self.__stop_date = None  # This is updated separately once the instance has been created
		self.__stop_time = None  # This is updated separately once the instance has been created
		self.__period_length = 0  # This is updated separately once the instance has been created
		self.__data_readings = []  # Initially empty until data readings are added
		self.__temp_max = None  # This will be calculated and assigned when data readings are added
		self.__humidity_average = None  # This will be calculated and assigned when data readings are added
		self.__staff = staff

	@property
	def start_date(self):
		return self.__start_date

	@property
	def start_time(self):
		return self.__start_time
	
	@property
	def staff(self):
		return self.__staff

	@property
	def stop_date(self):
		return self.__stop_date

	@stop_date.setter
	def stop_date(self, value):
		self.__stop_date = value

	@property
	def stop_time(self):
		return self.__stop_time

	@stop_time.setter
	def stop_time(self, value):
		self.__stop_time = value

	@property
	def period_length(self):
		return self.__period_length

	@period_length.setter
	def period_length(self, value):
		self.__period_length = value

	@property
	def temp_max(self):
		return self.__temp_max

	@property
	def humidity_average(self):
		return self.__humidity_average

	def add_data_reading(self, data_reading):
		"""
		This method is used to add a new data reading to this AccessPeriod class instance, you must use this method
		as it also updates the maximum temperature and humidity average as a new data reading is added

		:param data_reading: data reading to be added as instance of DataReading class

		:return: nothing
		"""
		# Add data reading to the data readings property
		self.__data_readings.append(data_reading)

		# Check if the temperature associated with this data reading is greater than the currently recorded maximum
		# temperature, note: if this is the first data reading added then the maximum temperature must be the
		# temperature from this reading
		if not self.temp_max:
			self.__temp_max = data_reading.temp_data
		elif data_reading.temp_data > self.temp_max:
			self.__temp_max = data_reading.temp_data

		# Update the humidity average to take account of this newly added data reading, note: if this is the first
		# data reading added then the average will be the humidity from this reading
		if not self.humidity_average:
			self.__humidity_average = data_reading.humidity_data
		else:
			self.calculate_humidity_average()

	def calculate_humidity_average(self):
		"""
		This method calculates the average of the humidity data held in the data readings list and updates the humidity
		average property with this value.

		:return:
		"""
		total = 0.0
		for data_reading in self.__data_readings:
			total += data_reading.humidity_data

		self.__humidity_average = total / len(self.__data_readings)

	def print_access_period(self):
		"""
		Print this access period to the console

		:return: nothing
		"""
		# First print the id of staff member
		print("Staff:    {0}".format(self.staff))


		# Print the start and end date and time for this access period
		print("Started:  {0} {1}".format(self.start_date, self.start_time))
		print("Stopped:  {0} {1}".format(self.stop_date, self.stop_time))

		

		# Second, print approximate length of the access period in seconds
		print("Length:   {0} seconds (approx)".format(self.period_length))

		# Third, print the maximum temperature recorded during this access period
		print("Max Temp: {0} degrees C".format(self.temp_max))

		# Fourth, print the humidity average recorded during this access period (to two decimal places)
		print("Hmdy Ave: {0:.2f} %".format(self.humidity_average))

		dewpoint = self.temp_max - ((100.0 - self.humidity_average) / 5.0)
		print("DewPoint: %d degrees C" %dewpoint)

		

		# Finally, print the full list of data readings for this access period
		print("Data Readings:")
		print("------------------------------------------------------------")
		for data_reading in self.__data_readings:
			print(data_reading)


class AccessPeriods:
	"""
	Class to contain a number of access periods as read from the supplied CSV data file when an instance of this
	class is instantiated
	"""
	def __init__(self, data_file):
		"""
		Initialiser - instance variables:
			__data_file: path to the CSV data file from which to read the access periods, as string, property with
			             no access
			__access_periods: List of AccessPeriod class instances created as the CSV data file is read, property with
						      no access

		:param data_file: path to the data_file, as string
		"""
		self.__data_file = data_file
		self.__access_periods = []  # Initially empty until read from CSV data file
		self.read_data_file()  # Read from the supplied CSV data file

	def read_data_file(self):
		"""
		Read from CSV data file property and add each read access period to the access periods list

		:return: nothing
		"""
		# Clear down any existing entries in access periods list
		self.__access_periods = []

		# Local variables to hold start dates and times of access periods
		start_date = None
		start_time = None

		# Local variable to hold stop dates and times of access periods
		stop_date = None
		stop_time = None

		# Local variable to hold period length of access periods
		period_length = 0

		# Local variable to hold the current access period object being read
		access_period = None

		# Open the CSV data file for reading and read each text line in sequence until end of file, note: each access
		# period consists of an ACCESS-STARTED line, any number of data reading lines and then an ACCESS-STOPPED line
		file = open(self.__data_file, "r")
		for line in file:
			# Remove any spurious end-of-line characters from this line as the file was written using UNIX style EOLs
			line = line.replace("\n", "")

			# Split this line according to the commas in the line
			entries = line.split(",")

			# If the first entry in the read line is the string "ACCESS-STARTED" then the next two entries are start
			# date and start time respectively, this is the start of a new access period object so instantiate one
			# locally
			if entries[0] == "ACCESS-STARTED":
				start_date = entries[1]
				start_time = entries[2]
				staff = entries[3]
				access_period = AccessPeriod(start_date, start_time, staff)

			# If the first entry in the read line is the string "ACCESS-STOPPED" then the next three entries are stop
			# date, stop time and period length respectively, this indicates the end of the data for this access
			# period so update the current access period object with the stop date and time and the period length and
			# then add this access period to the access periods list
			if entries[0] == "ACCESS-STOPPED":
				stop_date = entries[1]
				stop_time = entries[2]
				period_length = int(entries[3])  # Convert period length to an integer
				access_period.stop_date = stop_date
				access_period.stop_time = stop_time
				access_period.period_length = period_length
				self.__access_periods.append(access_period)

			# If the first entry in the read line is neither "ACCESS-STARTED" nor "ACCESS-STOPPED" then this must be a
			# data reading, so instantiate a data reading and add it to the access period object using its method
			# add_data_reading()
			if entries[0] != "ACCESS-STARTED" and entries[0] != "ACCESS-STOPPED":
				# First entry is the timestamp, the second entry is the temperature data and the third entry is the
				# humidity data, note: temperature and humidity need to be converted to floats
				timestamp = entries[0]
				temp_data = float(entries[1])
				humidity_data = float(entries[2])
				

				# Create new data reading instance
				data_reading = DataReading(timestamp, temp_data, humidity_data)

				# Add this to the access period instance using its add_data_reading() method
				access_period.add_data_reading(data_reading)

	def print_access_periods(self):
		"""
		Print all access periods to the console

		:return: nothing
		"""
		print()
		print("Access Periods from file: [{0}]".format(self.__data_file))
		print("===========================================================")

		if not self.__access_periods:
			print("***No access periods available***")
			print()
		else:
			for access_period in self.__access_periods:
				access_period.print_access_period()
				print()


# Program entrance function
def main():
	"""
	Main function
	"""
	print()
	print("PPW2 Desktop Application")
	print("---------------------------------------------------")

	# File name containing access periods
	data_file_name = "access_data.csv"

	# Instantiate an access periods instance and print it
	access_periods = AccessPeriods(data_file_name)
	access_periods.print_access_periods()

	# Exit application
	print("Finished")


# Invoke main() program entrance
if __name__ == "__main__":
	# execute only if run as a script
	main()
