admins = { }
modules_enabled = {
    "roster";
    "saslauth";
    "tls";
    "dialback";
    "disco";
    "version";
    "uptime";
    "time";
    "ping";
    "register";
}
modules_disabled = { }
allow_registration = true
c2s_require_encryption = true
s2s_require_encryption = false
c2s_ports = { 5224 }
s2s_ports = { 5271 }
authentication = "internal_hashed"
log = {
    info = "/mnt/c/Users/mitro/OneDrive - e-uvt.ro/Desktop/Proiect MAS/_V4_/prosody.log";
    error = "/mnt/c/Users/mitro/OneDrive - e-uvt.ro/Desktop/Proiect MAS/_V4_/prosody.err";
}
pidfile = "/mnt/c/Users/mitro/OneDrive - e-uvt.ro/Desktop/Proiect MAS/_V4_/prosody.pid"
data_path = "/mnt/c/Users/mitro/OneDrive - e-uvt.ro/Desktop/Proiect MAS/_V4_/prosody_data"

VirtualHost "localhost"
  ssl = {
      key = "/mnt/c/Users/mitro/OneDrive - e-uvt.ro/Desktop/Proiect MAS/_V4_/localhost.key";
      certificate = "/mnt/c/Users/mitro/OneDrive - e-uvt.ro/Desktop/Proiect MAS/_V4_/localhost.crt";
  }