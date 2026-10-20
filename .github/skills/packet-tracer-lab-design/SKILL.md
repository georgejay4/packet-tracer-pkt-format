---
name: packet-tracer-lab-design
description: "Design and generate original Cisco Packet Tracer labs from natural-language or text prompts. Use when turning a networking scenario, assignment brief, or lab idea into a topology, device configurations, student instructions, a .pkt file, or a scored .pka activity in this repository."
argument-hint: "Describe the lab scenario, learning goals, requirements, and desired output (.pkt, .pka, or choose for me)"
user-invocable: true
---

# Design Packet Tracer Labs from Prompts

Turn a user's written networking scenario into a coherent, buildable Packet
Tracer lab using this repository's authoring tools. Deliver the requested
`.pkt` or `.pka` artifact, not just a proposed topology.

## Workflow

1. **Choose the configuration mode.** Determine what state the lab should be
   in when it opens:
   - **Ready-to-run/reference lab:** Preconfigure the requested interfaces,
     addressing, routing, and services so the intended behavior is available
     immediately. Validate the specified behavior and include useful
     operating or verification notes. For a test lab, fully configure the
     scenario and validate the behavior or test case it is intended to
     demonstrate; do not leave any required setup for the user.
   - **Learner exercise:** Provide the topology and any requested addressing
     plan or hints, but leave the named learning objectives unconfigured.
     Include concise student tasks and success criteria. Do not put the
     instructor solution into the learner file. The standard learning-lab
     deliverable also includes a separate, configured `_COMPLETED` reference
     copy beside the learner file and guide.
   - **Instructor bundle:** Create additional instructor-only deliverables
     beyond the standard learner file, guide, and completed reference copy
     only when the user asks for them.

   **Mandatory clarification gate:** Before designing or generating any lab,
   confirm that the user has explicitly made the lab type clear:
   - A **learning lab** is for student practice; the stated learning objectives
     remain unconfigured in the learner file, with a guide, a configured
     `_COMPLETED` copy, and a completed-state SVG.
   - A **fully configured test/reference lab** opens ready to use for testing
     or demonstration and goes in the dated `Generated Labs` folder with its
     configured file and topology SVG.

   Words such as “lab,” a named protocol, “complete,” or a request for a `.pkt`
   alone do not make the type clear. Do not infer it from earlier defaults,
   presumed audience, file format, or the fact that the request contains a
   test or learning topic. If the current request does not unambiguously say
   which type is wanted, stop and ask the user to choose before proceeding.
   For example: **“Should this be (1) a learning lab with the target
   configuration left for students, or (2) a fully configured test/reference
   lab that opens ready to use?”** Use the ask-user form when available. Do
   not make files, select a folder, or begin topology design until the user
   clarifies. If neither option fits, let the user specify the intended type.
2. **Extract the requirements.** Identify learning goals and level (if
   applicable), device inventory and links, protocols or services, addressing
   constraints, learner-configured items, expected end state, requested
   instructions, grading needs, output format, and output location.
3. **Resolve other material ambiguity.** After the mandatory lab-type gate,
   ask a concise question when an unanswered choice would change the topology, addressing, learning
   objective, grading, or file type. Otherwise use conventional defaults and
   state them in the final summary. Treat explicit prompt constraints as
   authoritative.
4. **Choose the artifact.**
   - Use `.pkt` for a configured demonstration, reference topology, or
     unscored learner topology.
   - Use `.pka` when the user wants Activity Wizard instructions and
     Check Results scoring. A learning exercise does not by itself imply `.pka`.
   - If the user leaves the format open, choose based on the intended use and
     mention why. Do not add grading to a `.pkt` or make a `.pka` unless useful
     for the stated objective.
5. **Design the topology before building.** Write down the device inventory,
   unique names, adjacency list, interface assignments, addressing plan,
   configuration responsibilities, and expected connectivity. Implement the
   requested links exactly; do not add extra links or reuse another lab's
   addressing plan without being asked.
6. **Check repository capabilities.** Read `docs/LAB_AUTHORING_DEFAULTS.md`
   and the relevant references before generation:
   - `docs/CAPABILITIES.md` and `docs/CONFIGURATION.md` for `.pkt` authoring.
   - `docs/PKA_GENERATION.md` and `docs/ACTIVITY.md` for scored activities.
   - `tools/device_templates.json` for supported device and module models.
   Verify that every selected model and interface is supported; never guess a
   port name or silently substitute a different model. Verify the installed
   expansion-module bay as well as its model: on a Cisco 2911,
   `FastEthernet0/1/x` maps to the second `eInterfaceCard` bay (absolute
   zero-based `slot=1`). `Lab.install_module(bay=0)` chooses the first empty bay;
   it does not mean absolute slot zero. Confirm the populated bay and cable
   endpoint names in the saved file. Keep each generated port's
   `MACADDRESS` equal to its `BIA`; differing values become explicit IOS
   `mac-address` overrides in Packet Tracer's running configuration.
7. **Build the requested artifact.**
   - For `.pkt`, use `tools/lab_api.py` (`load_templates`, `Lab`, and
     `Layout`) with `tools/network_seed.xml`. Prune inherited seed devices for
     a clean lab unless the prompt asks to keep them. Use `Layout` to place
     devices with readable spacing; pass each returned placement's `x` and `y`
     to `Lab.add_device`. In a ready-to-run lab, add requested device
     configuration and endpoint IP settings with `ios_config` and `pc_ip`. For
     fully configured test labs and completed learning-lab copies, add a useful
     IOS `description` to every interface receiving configuration, including
     routed ports, switchports, VLAN SVIs, and loopbacks. Describe the peer,
     VLAN/LAN purpose, or loopback role; include the subnet when useful. Do not
     add descriptions to untouched/default interfaces. In every lab, ensure
     each IOS router/switch hostname matches its Packet
     Tracer display name; this baseline identity does not configure the
     learning objective. Do not include `ip domain-name` or
     `no ip domain-name` in device default configurations unless a lab
     explicitly requires domain-name configuration. In a learner exercise,
     omit configuration the student is meant to supply and put proposed values
     in labels or instructions. Connect only planned links and save the file.
   - For `.pka`, write a JSON topology spec and run:
     `python3 tools/make_scored_lab.py --out <output.pka> --spec <spec.json> --prune-seed`.
     The spec uses `devices` (model, name, optional `x`, `y`, `config`,
     `pc_ip`, and `install`), `links` (`a`, `aport`, `b`, `bport`, and optional
     `kind`/`dce`), and optional `instructions` (one HTML page or a list of
     HTML pages). Its initial network is unconfigured and its answer network
     is configured; use it for scored learner activities only when that
     behavior is wanted. Review generated scoring against the learner task.
     Include only original, prompt-relevant instructions and answer
     configuration. Do not set an Activity Wizard password unless explicitly
     requested.
   - Save learner labs under `/Users/george/Desktop/PTLABS/Learning Labs` when
     that directory is available, unless the user requests another location.
     Create one new folder per learner lab, named
     `<NNN> <Short Lab Summary>` (for example, `001 RIP Configuration`). Start
     at `001`; choose the next number by incrementing the highest existing
     three-digit numbered lab folder inside `Learning Labs` by one, and never
     reuse a number or overwrite an existing folder. Keep the learner `.pkt` or
     `.pka` and its guide together in that folder. Also create a configured
     reference copy of every learner lab in the same folder, with `_COMPLETED` appended
     to the learner lab's filename stem (for example,
     `RIP_5_Router_R1_Full_Mesh_Learning_COMPLETED.pkt`). Keep its format and
     topology the same and configure the full solution described by the guide.
     Also create an original SVG network diagram showing the completed
     topology, device names, link interfaces and addresses, LANs, and relevant
     routing/configuration details. Save it in the same numbered folder as
     `<lab-name>_COMPLETED.svg`; make it clear that it depicts the completed
     state and keep all diagram details consistent with the guide and completed
     Packet Tracer file.
   - Save fully configured test labs under
     `/Users/george/Desktop/PTLABS/Generated Labs` when available, unless the
     user requests another location. Create a separate folder named
     `<YYYY-MM-DD> <Short Lab Summary>` using the local date the lab is
     generated (for example, `2026-10-20 OSPF Route Failover`). Do not overwrite
     an existing folder; if the same date and summary already exist, append a
     short distinguishing suffix. Put the final configured `.pkt` or `.pka`
     and an original SVG network diagram in that folder. Name the diagram
     `<lab-name>_TOPOLOGY.svg`; show the configured devices, links, interface
     names and addresses, subnets, and the relevant feature or test state.
     Keep the diagram consistent with the saved lab and any requested test
     procedure. A learner guide and `_COMPLETED` copy are not required for
     these already-configured test labs unless requested.
     Ready-to-run labs need not use the numbered learner-lab convention or
     receive a separate completed copy unless requested.
     Put temporary specs or helper code in a task-specific temporary location,
     not among project sources. Do not overwrite an existing output without
     checking first.
8. **Write the learning guide.** For every learner exercise, create an
   accompanying Markdown guide in the same numbered lab folder as the
   `.pkt`/`.pka`, named `<lab-name>_GUIDE.md`. Include, in this order:
   - Purpose, prerequisites, learning objectives, and what is intentionally
     left unconfigured in the learner file.
   - Proposed topology and a device/interface/address table. For every link,
     show both endpoint device/interface names, endpoint addresses, prefix or
     mask, and network. Include loopback addresses and any module, switchport,
     VLAN, or SVI details that affect addressing.
   - A numbered, device-by-device CLI walkthrough in a valid command order.
     Show commands to enter configuration modes, configure the listed
     interfaces and required Layer 2 details, enable links, and configure the
     requested routing protocols/services. Keep commands consistent with the
     exact device models, ports, addressing plan, and task. Put this solution
     in the companion guide, not in the learner `.pkt` or student-facing `.pka`
     instructions unless the user explicitly asks otherwise.
   - A verification section with exact show/test commands, where to run them,
     expected results (neighbors, routes, interface states, pings, or other
     task-specific outcomes), and a short troubleshooting sequence for likely
     failures.
   - A clear completion checklist and any assumptions or Packet Tracer limits.
     Mention the sibling completed-state SVG diagram.

   Distinguish instructional commands from checks actually run against the
   generated artifact: do not report expected results as observed results.
   The configured `_COMPLETED` reference file is in addition to, never a
   substitute for, the learning guide. Keep the learner file unconfigured for
   the requested learning objectives.
9. **Validate the saved file and guide.** Run:
   - `python3 tools/check_layout.py <output>` and resolve reported overlaps or
     off-page placements.
   - `python3 tools/audit_links.py <output>` and ensure every link endpoint
     refers to an existing device and a real interface on that device. Resolve
     configuration findings for ready-to-run labs. In learner exercises,
     unconfigured learner-facing ports may be intentional; verify their
     endpoints and labels and report those findings rather than adding the
     answer configuration.
   - Decode and inspect the saved file with `pkt_core` / `Lab` to confirm its
     root type, device names and models, link count, and (for `.pka`) activity
     instructions and scoring sections. Confirm it opens and its actual state
     matches the design; do not present a generated file as runtime- or
     connectivity-verified unless that check was actually performed.
   - Check every guide topology/address row against the generated file and
     every CLI interface against the selected model/module. Check that
     configuration commands are ordered correctly and that verification
     commands and stated expected outcomes correspond to the design.
   - Parse each generated SVG as XML and check its device, interface, address,
     subnet, and routing/feature labels against the appropriate saved
     Packet Tracer file and guide or test procedure. For test labs, validate
     the documented test behavior against the configured artifact and clearly
     distinguish actual checks performed from expected behavior.
10. **Report the result.** State whether this is ready-to-run or a learner
    exercise, and give the artifact and companion guide paths, format, topology
    and addressing summary, student task/learning goals (if applicable),
    validation commands and outcomes, and any assumptions or unverified
    runtime behavior.

## Authoring rules

- Follow `docs/LAB_AUTHORING_DEFAULTS.md`: use copper straight-through for all
  links unless the user explicitly requests another cable type or copper is
  unsupported by the required devices. A shortage of built-in Ethernet ports
  is not a reason to substitute serial; check and install a supported Ethernet
  module, and configure its Layer 2 ports/VLAN SVIs as required.
- Match each module's actual occupied bay to its interface numbering. For a
  Cisco 2911 `HWIC-4ESW` using `FastEthernet0/1/x`, install in absolute bay
  `slot=1` and verify that the module occupies that bay before relying on those
  cable endpoints.
- Keep per-port `MACADDRESS` equal to `BIA` and verify generated IOS
  `show running-config` output contains no unintended `mac-address` overrides.
- Include native link labels with endpoint names/interfaces and the carried
  subnet; `Lab.link()` adds these by default.
- Give every device a unique, descriptive name. Use `Lab.device_names()` or
  prune the seed before choosing names to avoid collisions.
- Plan addressing with non-overlapping networks and valid host/gateway
  addresses. Configure routing and interface state needed for the stated
  connectivity goals. Avoid claiming that a topology works based only on
  cables being present.
- In learner exercises, leave interfaces, protocols, and services the learner
  is meant to configure out of the running-config. Show proposed interface
  addressing and other reference values in Packet Tracer workspace labels or
  instructions instead. A link audit may flag intentionally unconfigured
  learner ports; report that as expected rather than adding the answer config.
- For CCNA/CCNP-style practice, include a concise student task and meaningful
  verification goals when requested or useful. Keep prompts, addressing, and
  any grading aligned, and do not turn a practice lab into a scored activity
  unless requested or clearly appropriate.
- Do not invent unsupported Packet Tracer models, modules, protocols,
  interfaces, or grading behavior. If the prompt depends on an unsupported
  capability, explain the limitation and offer a supported alternative.
- Create original practice materials. Do not use this workflow to extract or
  provide answer keys for an existing graded assessment, bypass assessment
  controls, or misrepresent unverified results.
