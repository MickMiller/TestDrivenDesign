test_commentPump00_Status.cmd Pump Status
send_cmd_ignore_response,P00S1,$A	## 1st time result may change
test_equal,P00S1,$A`S