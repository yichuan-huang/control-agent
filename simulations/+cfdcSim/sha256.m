function digest=sha256(bytes)
%SHA256 Fingerprint exact source bytes for the local run record.
md=java.security.MessageDigest.getInstance('SHA-256');
md.update(typecast(uint8(bytes(:)),'int8'));
raw=typecast(int8(md.digest()),'uint8');
digest=lower(reshape(dec2hex(raw,2).',1,[]));
end
