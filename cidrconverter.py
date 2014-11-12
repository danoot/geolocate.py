def cidr2range(s):
	start,range = s.split('/')
	range = 2**(32-int(range))-1
	a,b,c,d = start.split('.')
	a = int(a)*256**3
	b = int(b)*256**2
	c = int(c)*256
	d = a+b+c+int(d)
	return (d,d+range)

with open('vlans') as f:
	for line in f.readlines():
		a,b = line.strip('\n').split(' ',1)
		a = cidr2range(a)
		print "%s\t%s\t%s" %(a[0],a[1],b)
