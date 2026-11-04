-- DDON postdissector

-- declare some Fields to be read
tcp_src_f = Field.new("tcp.srcport")
tcp_dst_f = Field.new("tcp.dstport")
tcp_payload_f = Field.new("tcp.payload")
tcp_len_f = Field.new("tcp.len")
tcp_stream_f = Field.new("tcp.stream")
tcp_seq_f = Field.new("tcp.seq")
tcp_ack_f = Field.new("tcp.ack")

-- declare DDON protocol
ddon_proto = Proto("ddon","DDON Postdissector")

-- create the fields for the DDON "protocol"
src_F = ProtoField.string("ddon.src","Source")
dst_F = ProtoField.string("ddon.dst","Destination")
conv_F = ProtoField.string("ddon.conv","Conversation")
payload_F = ProtoField.string("ddon.payload","Payload")
datasize_F = ProtoField.string("ddon.datasize", "Datasize")
buffer_size_F = ProtoField.string("ddon.buffersize", "Buffersize")

-- add the fields to the protocol
ddon_proto.fields = {src_F, dst_F, conv_F, payload_F, datasize_F, buffer_size_F}

datasize_s2c = 0
buffer_s2c = 0
shouldReadHeader_s2c = true

datasize_c2s = 0
buffer_c2s = 0
shouldReadHeader_c2s = true


-- create a function to "postdissect" each frame
function ddon_proto.dissector(buffer,pinfo,tree)

    -- obtain the current values the protocol fields
    local tcp_src = tcp_src_f().value
    local tcp_dst = tcp_dst_f().value
	local tcp_payload = tcp_payload_f()
    local tcp_len = tcp_len_f().value
    local tcp_stream = tcp_stream_f().value
    local tcp_seq = tcp_seq_f().value
    local tcp_ack = tcp_ack_f().value

    -- DDON client <-> server communication
        if tcp_payload and tcp_stream == 11 and (tcp_src == 52000 or tcp_src == 52100 or tcp_dst == 52000 or tcp_dst == 52100) then
            local subtree = tree:add(ddon_proto,"DDON Protocol Data")
     
            local src = ""
            local dst = ""
            if tcp_src == 52000 or tcp_src == 52100 then
             src = "S"
             dst = "C"
            end
            if tcp_dst == 52000 or tcp_dst == 52100 then
             src = "C"
             dst = "S"
            end
            local conv = src  .. "2" .. dst
            subtree:add(src_F,src)
            subtree:add(dst_F,dst)
            subtree:add(conv_F,conv)
     
            local payload = tostring(tcp_payload):gsub(":", "")
            subtree:add(payload_F,payload)
     
            if conv == "S2C" then
             -- New stream
             if tcp_seq == 1 then
                 buffer_s2c = 0
                 datasize_s2c = 0
                 shouldReadHeader_s2c = true
             end
     
             -- "reset"
             if shouldReadHeader_s2c then
                 local dataSizeBytes = payload:sub(1, 4)
                 local datasize = tonumber(dataSizeBytes, 16)
                 datasize_s2c = datasize
                 buffer_s2c = 0
                 shouldReadHeader_s2c = false
             end
     
             if not shouldReadHeader_s2c then
                 subtree:add(datasize_F,tostring(datasize_s2c))
                 if buffer_s2c >= datasize_s2c then
                     subtree:add(buffer_size_F,tostring(buffer_s2c))
                     
                     shouldReadHeader_s2c = true
                 else
                     buffer_s2c = buffer_s2c + tcp_len
     
                     subtree:add(buffer_size_F,tostring(buffer_s2c))
                 end
             end
            end
     
            if conv == "C2S" then
             -- New stream
             if tcp_seq == 1 then
                 buffer_c2s = 0
                 datasize_c2s = 0
                 shouldReadHeader_c2s = true
             end
     
             -- "reset"
             if shouldReadHeader_c2s then
                 local dataSizeBytes = payload:sub(1, 4)
                 local datasize = tonumber(dataSizeBytes, 16)
                 datasize_c2s = datasize
                 buffer_c2s = 0
                 shouldReadHeader_c2s = false
             end
     
             if not shouldReadHeader_c2s then
                 subtree:add(datasize_F,tostring(datasize_c2s))
     
                 if buffer_c2s >= datasize_c2s then
                     subtree:add(buffer_size_F,tostring(buffer_c2s))
                     
                     shouldReadHeader_c2s = true
                 else
                     buffer_c2s = buffer_c2s + tcp_len
     
                     subtree:add(buffer_size_F,tostring(buffer_c2s))
                 end
     
             end
            end
        end
end

-- register our protocol as a postdissector
register_postdissector(ddon_proto)
