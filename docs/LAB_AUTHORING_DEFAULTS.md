# Lab authoring defaults

Use these defaults when creating new labs in this repository. A request-specific
topology, addressing plan, or cable type takes precedence.

## Configuration mode

Decide what state the lab should be in when it opens:

- **Ready-to-run/reference lab:** configure the requested interfaces,
  addressing, routing, and services so the intended behavior is available
  immediately. For test labs, fully configure the scenario and validate the
  intended behavior or test case; do not leave required setup for the user.
- **Learner exercise:** provide the requested topology and addressing hints,
  but leave the target configuration for the student. Include clear tasks and
  success criteria. Do not put the solution in the learner file. Include a
  separate configured `_COMPLETED` reference file beside the learner file and
  guide.
- **Instructor bundle:** produce additional instructor-only deliverables
  beyond the learner file, guide, and completed reference file only when
  requested.

“Complete lab” can describe a finished deliverable without specifying whether
it should be preconfigured. Therefore, before designing or generating any lab,
require an explicit, unambiguous choice between a learning exercise (target
configuration left for students) and a fully configured test/reference lab
(opens ready to use). Do not infer the type from words such as “lab,” a
protocol name, “complete,” file format, prior defaults, or an assumed audience.
If the request does not clearly identify the type, stop and ask the user to
choose; do not begin topology design or create files until they clarify. Use the
ask-user form when available. `.pkt` versus `.pka` is a separate choice;
learning activities do not automatically need scoring.

For IOS routers and switches, set the running-config `hostname` to the same
value as the device's Packet Tracer display name. This is a baseline identity
setting, not the learner's interface or routing solution. Do not include
`ip domain-name` or `no ip domain-name` commands in any device's default
configuration; domain-name configuration is omitted unless a lab explicitly
requires it.

In fully configured test labs and `_COMPLETED` learning-lab copies, include a
useful IOS `description` on every interface that receives configuration:
routed interfaces, switchports, VLAN SVIs, and loopbacks. Describe the
connected peer, VLAN/LAN purpose, or loopback role; include the subnet when
helpful. Do not add descriptions to untouched/default interfaces. Include these
descriptions in the documented configuration walkthrough as well.

For every learner exercise, create a new folder under
`/Users/george/Desktop/PTLABS/Learning Labs` when available, unless the user
requests another location. Name it `<NNN> <Short Lab Summary>`, starting at
`001` and incrementing from the highest existing three-digit numbered lab
folder in `Learning Labs` (for example, `001 RIP Configuration`, then
`002 OSPF Multi-Area`). Do not reuse a number or overwrite an existing folder.
Keep the learner `.pkt` or `.pka` and its
companion `<lab-name>_GUIDE.md` together in that folder. Also include a
configured reference copy of each learner lab in the same folder, with
`_COMPLETED` appended to the learner filename stem (for example,
`RIP_5_Router_R1_Full_Mesh_Learning_COMPLETED.pkt`). It should retain the same
format and topology, and apply the full solution documented in the guide.
Also create an original SVG network diagram named
`<lab-name>_COMPLETED.svg` in the same numbered folder. Show the completed
topology with device names, interface endpoints, interface addresses and
subnets, LANs, and relevant routing/configuration details. Label it as the
completed state, and verify it matches the guide and completed `.pkt`/`.pka`.
Ready-to-run/reference labs are not numbered and do not need a separate
completed learner copy unless requested. Fully configured test labs use the
dated folder and topology-diagram convention below.

Fully configured test labs belong in
`/Users/george/Desktop/PTLABS/Generated Labs` when available, unless another
location is requested. Create a folder named `<YYYY-MM-DD> <Short Lab Summary>`
using the local date generated (for example, `2026-10-20 OSPF Route Failover`).
If a folder with the same date and summary already exists, do not overwrite it;
append a short distinguishing suffix. Include the final configured `.pkt` or
`.pka` and an original `<lab-name>_TOPOLOGY.svg` diagram. The diagram should
show the configured topology, devices, interfaces, addressing, subnets, and
relevant feature/test state. Keep it consistent with the saved lab and any
test procedure. A learning guide and separate completed copy are unnecessary
for these already-configured test labs unless requested.

For generated diagrams in either lab type, parse the SVG and check that device,
interface, address, subnet, and protocol/feature labels agree with the saved
Packet Tracer file and accompanying guide or test procedure.

Start the guide with the proposed topology and a complete
device/interface/addressing table, then provide an ordered CLI walkthrough,
verification commands with expected outcomes, troubleshooting tips, and a
completion checklist. Include the instructional solution in the guide and
completed reference file, never by preconfiguring the learner file or exposing
the solution in student-facing activity instructions.

## Topology and cabling

- Implement the requested topology and adjacency matrix exactly; do not add
  extra router links or reuse an earlier lab's addressing plan unless asked.
- Use copper straight-through cables for every link by default. Use serial or
  another cable type only when the user explicitly requests it or the required
  devices cannot support copper.
- Do not switch to serial just because a router has run out of built-in
  Ethernet ports. Add a supported Ethernet module and configure its Layer 2
  ports/VLAN SVIs as needed, or ask before changing the requested topology.
- Add expansion modules when the topology needs more interfaces than the
  device's built-in ports provide. For Cisco 2911 routers, use the
  `HWIC-4ESW` when additional Ethernet switchports are needed. Use an authentic
  Packet Tracer module record, verify the installed bay and interface names,
  and configure its Layer 2 ports/VLAN SVIs accordingly.
- Keep every generated port's `<MACADDRESS>` equal to its `<BIA>`. Distinct
  per-port identities are required, but differing values make Packet Tracer
  write explicit `mac-address` overrides into IOS `show running-config`.
- On a Cisco 2911, `FastEthernet0/1/x` refers to the HWIC-4ESW in the second
  `eInterfaceCard` bay (absolute zero-based slot index `1`). In `Lab.install_module`,
  `bay=0` means “first empty bay,” not “absolute bay 0”; use `slot=1` when that
  specific interface numbering is required. Verify the populated bay in the
  saved file against every cable endpoint: a module in a different bay can
  leave cable port names referring to the wrong physical slot and make Packet
  Tracer reject the file.

## Workspace labels and deliverables

- Label each cable in the Packet Tracer logical workspace with both endpoint
  device/interface names and the subnet carried by that link. `Lab.link()`
  creates native Packet Tracer workspace notes automatically and resolves the
  subnet from configured interfaces, including access VLAN SVIs and end-device
  NICs. See [CAPABILITIES.md](./CAPABILITIES.md) for explicit overrides and
  opt-outs.
- When a diagram or lab instructions are requested, include them with the
  Packet Tracer file and keep their topology/address information consistent
  with the saved lab.
- Validate cable endpoint names against the actual device instances, run the
  link audit, and preserve a working prior file when replacing a lab that has
  already been verified.
