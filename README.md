# The-New-Internet
Our attempt to create a new internet
* Implementation of a reliable transfer service on top of the UDP/IP protocol.
* Designning a service that guarantees the arrival of datagrams in the correct order on top of the UDP/IP protocol.
---

## To Do ##

- [X] Client side ---> (*Mostafa*)
- [X] Server side ---> (*Mostafa*)
- [X] Server with multi-threading support ---> (*Mostafa*)
- [ ] Bug with scaling (When the file is large, the file received at the client is much smaller than the actual file. Most likely an issue with parsing the file in the sneder).
- [ ] Testing Multiple Clients at the same time
- [ ] Stop and wait ---> (*Essam*)
- [X] Selective repeat ---> (*Essam*)
- [ ] Go back-N ---> (*Essam*)
- [ ] PLP ---> (*Essam*)
- [ ] Corrupted data ---> (*Essam*)
- [ ] Data class ---> (*Essam*)
- [ ] Checksum
- [ ] Bonus
