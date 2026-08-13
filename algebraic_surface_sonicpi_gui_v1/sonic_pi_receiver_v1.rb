# Algebraic Surface — Sonic Pi realtime receiver
#
# Paste this whole buffer into a Sonic Pi buffer and hit Run once, then
# leave it running. It listens for OSC cues sent by
# algebraic_surface_sonicpi_gui_v1/gui_v1.py and turns each surface's
# Laplace-Beltrami mode set into a live chord of decaying sine partials.
#
# Setup (once): Sonic Pi Preferences -> IO -> "Enable OSC Server" ON.
# Default OSC-in port is 4560, matching the GUI's default target.

set_volume! 0.7

# Persists across buffer re-runs so the panic loop can always reach every
# partial that is still sounding, even ones triggered by an earlier run.
$algebraic_nodes ||= []

live_loop :algebraic_modes do
  msg = sync "/osc*/algebraic/modes"
  count = msg[0].to_i
  values = msg[1..-1]

  count.times do |i|
    base = i * 4
    freq  = values[base]
    decay = values[base + 1]
    amp   = values[base + 2]
    pan   = values[base + 3]

    in_thread do
      use_synth :sine
      node = play hz_to_midi(freq),
        amp: amp * 0.5,
        pan: pan,
        attack: 0.01,
        release: decay
      $algebraic_nodes << node
    end
  end
end

live_loop :algebraic_silence do
  sync "/osc*/algebraic/silence"
  nodes, $algebraic_nodes = $algebraic_nodes, []
  nodes.each { |node| node.kill if node.respond_to?(:kill) }
end
