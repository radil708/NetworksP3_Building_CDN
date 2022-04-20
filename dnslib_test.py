import dnslib
import binascii

def main():
    data_test = b'\x07\xf8\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x02\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08\xede$\x97\x1d\xd8\x92\xf4'.hex()
    data_test = binascii.unhexlify(data_test)
    new_test = dnslib.DNSRecord.question("google.com")
    parsed = dnslib.DNSRecord.parse(new_test.pack())
    #print(type(parsed.get_q))
    y = parsed.get_q()
    print(y, type(y))
    #
    print("STOP")
    print(y.qname.__str__(), type(y.qname.__str__()))
    #get questions
    #print(parsed.questions)
    #ype is DNSQuestion
    #print(type(parsed.questions[0]))
    x = parsed.questions[0].__str__
    print(x)
main()
