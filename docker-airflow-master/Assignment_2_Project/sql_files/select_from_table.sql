SELECT * FROM hotel_bookings WHERE RESERVATION_STATUS = 'Canceled'  INTO OUTFILE '/data_files_mysql/reservation_cancellations.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';