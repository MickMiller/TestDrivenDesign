test_commentPump03_SwRev.cmd Pump Software Revision Number
send_cmd_ignore_response,P03S1,$A	## Result starts $A not $B
test_equal,P03@,$ASW04.01M