test_commentPump00_SwRev.cmd Pump Software Revision Number
send_cmd_ignore_response,P00S1,$A	## Result starts $A not $B
test_equal,P00@,$ASG04.00>