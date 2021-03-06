#The MIT License (MIT)
#
#Copyright (c) 2015 JP Senior (jp.senior@gmail.com)
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
#


import argparse
import sys

parser = argparse.ArgumentParser(description=
                                 "A tool that converts an HTML file to a copy-and-paste Netscaler configuration"
                                 " script, \n Allowing for 255-line maximum STRING definitions, while escaping "
                                 "double-quotes.\nWARNING: You must copy the text without new line wrapping!\n"
                                 "This script will output an 'output.txt' file for you to copy-paste from.")
parser.add_argument('--output', help="Specify an output type.", choices=["GUI","CLI"], default="GUI")
parser.add_argument('filename', nargs='?', help="Specify an HTML file to build a response for")

#Allow a user to specify a filename or stdin to convert documents
args = parser.parse_args()
if args.filename:
    string = open(args.filename).read()
elif not sys.stdin.isatty():
    string = sys.stdin.read()
else:
    parser.print_help()

# PEP8 error expected.
try:
    string
except NameError:
    parser.print_help()
    exit()


# Escape double quotes
string = string.replace('"', '\\"')
# Split data up into 250-character chunks (Netscaler has a maximum of 255)
text = [string[item:item+250] for item in range(0, len(string), 250)]

response = list()
#503 service unavailable messages will not be cached by a browser.
response.append('"HTTP/1.1 503 Service Unavailable\\r\\n\\r\\n" + ')
for item in text:
    line = item.split('\n')
    for entry in line:
        #Remove blank lines, it makes the Netscaler parser error out
        if entry.split():
            response.append('"%s" + ' % entry)

response.append('""')
with open("output.txt", "wb+") as f:
    for item in response:
        f.write(item)


#Some silly copy-paste stuff for end users.
if args.output == 'GUI':
    print ''.join(response)
elif args.output == 'CLI':
    print 'add responder action MaintenancePage_Action respondwith q{%s}' % (''.join(response))
    print 'add responder policy MaintenancePage_Policy MaintenancePage_Action'

