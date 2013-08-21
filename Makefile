all: thrift

thrift:
	mkdir atlasnode/protocol || true
	thrift --gen py:new_style,utf8strings -out atlasnode/protocol Protocols/Node.thrift