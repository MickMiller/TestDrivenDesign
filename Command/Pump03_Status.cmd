test_commentPump03_Status.cmd Pump Status
send_cmd_ignore_response,P03S1,$A	## 1st time result may change
test_equal,P03S1,$A`S