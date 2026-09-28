import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:cast/cast.dart';

void main() {
  runApp(const MyRadioApp());
}

class MyRadioApp extends StatelessWidget {
  const MyRadioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'My Radio',
      theme: ThemeData(
        brightness: Brightness.dark,
        useMaterial3: true,
      ),
      home: const RadioHomePage(),
    );
  }
}

class RadioHomePage extends StatefulWidget {
  const RadioHomePage({super.key});

  @override
  State<RadioHomePage> createState() => _RadioHomePageState();
}

class _RadioHomePageState extends State<RadioHomePage> {
  final AudioPlayer _player = AudioPlayer();

  bool _isPlaying = false;
  bool _isLoading = false;
  double _volume = 1.0;

  final String radioUrl = 'https://das-radio.onrender.com';
  
  List<CastDevice> _castDevices = [];
  bool _isScanning = false;

  @override
  void initState() {
    super.initState();

    _player.playerStateStream.listen((state) {
      if (!mounted) return;

      setState(() {
        _isPlaying = state.playing;
        _isLoading = !state.playing &&
            (state.processingState == ProcessingState.loading ||
                state.processingState == ProcessingState.buffering);
      });
    });
  }

  Future<void> _toggleRadio() async {
    try {
      if (_player.playing) {
        await _player.stop();
        if (!mounted) return;
        setState(() {
          _isLoading = false;
          _isPlaying = false;
        });
        return;
      }

      setState(() {
        _isLoading = true;
      });

      await _player.setUrl(radioUrl);
      await _player.setVolume(_volume);
      await _player.play();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _isPlaying = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Radio connect nahi ho paya: $e')),
      );
    }
  }

  Future<void> _scanForCastDevices() async {
    setState(() {
      _isScanning = true;
      _castDevices.clear();
    });

    try {
      final CastDiscoveryService discoveryService = CastDiscoveryService();
      List<CastDevice> devices = await discoveryService.search();
      setState(() {
        _castDevices = devices;
      });
    } catch (e) {
      print("Cast scan error: $e");
    } finally {
      if (mounted) {
        setState(() {
          _isScanning = false;
        });
      }
    }
  }

  void _showCastDialog() {
    _scanForCastDevices();
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Google Cast Devices'),
          content: SizedBox(
            width: double.maxFinite,
            height: 250,
            child: StatefulBuilder(
              builder: (context, setStateBuilder) {
                return Column(
                  children: [
                    if (_isScanning)
                      const LinearProgressIndicator(),
                    const SizedBox(height: 10),
                    Expanded(
                      child: _castDevices.isEmpty
                          ? Center(
                              child: Text(_isScanning
                                  ? 'Searching for speakers/TVs...'
                                  : 'No Cast devices found'),
                            )
                          : ListView.builder(
                              itemCount: _castDevices.length,
                              itemBuilder: (context, index) {
                                final device = _castDevices[index];
                                return ListTile(
                                  leading: const Icon(Icons.cast, color: Colors.indigoAccent),
                                  title: Text(device.name),
                                  subtitle: Text(device.host),
                                  onTap: () {
                                    Navigator.pop(context);
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('Connected to ${device.name}')),
                                    );
                                  },
                                );
                              },
                            ),
                    ),
                  ],
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _changeVolume(double value) async {
    setState(() {
      _volume = value;
    });
    await _player.setVolume(value);
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.cast, color: Colors.white),
            onPressed: _showCastDialog,
            tooltip: 'Cast to Device',
          ),
        ],
      ),
      extendBodyBehindAppBar: true,
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF26345C),
              Color(0xFF111522),
              Color(0xFF07090F),
            ],
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Container(
              width: 420,
              margin: const EdgeInsets.all(24),
              padding: const EdgeInsets.symmetric(
                horizontal: 28,
                vertical: 38,
              ),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.08),
                borderRadius: BorderRadius.circular(28),
                border: Border.all(
                  color: Colors.white.withOpacity(0.12),
                ),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 105,
                    height: 105,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        colors: [
                          Color(0xFF6C63FF),
                          Color(0xFF9B5CFF),
                        ],
                      ),
                    ),
                    child: const Center(
                      child: Text(
                        '📻',
                        style: TextStyle(fontSize: 45),
                      ),
                    ),
                  ),
                  const SizedBox(height: 22),
                  const Text(
                    'My Radio',
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Music • Anytime • Live',
                    style: TextStyle(
                      color: Color(0xFFAEB6CC),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 22),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 13,
                      vertical: 7,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0x1F22C55E),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.circle,
                          size: 8,
                          color: _isPlaying
                              ? const Color(0xFF35E879)
                              : Colors.grey,
                        ),
                        const SizedBox(width: 7),
                        Text(
                          _isPlaying ? 'LIVE' : 'OFFLINE',
                          style: TextStyle(
                            color: _isPlaying
                                ? const Color(0xFF5EE88A)
                                : Colors.grey,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 25),
                  // Sirf Play/Pause button aur Volume slider
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      GestureDetector(
                        onTap: _isLoading ? null : _toggleRadio,
                        child: Container(
                          width: 68,
                          height: 68,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: const LinearGradient(
                              colors: [
                                Color(0xFF6C63FF),
                                Color(0xFF9B5CFF),
                              ],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF6C63FF)
                                    .withOpacity(0.4),
                                blurRadius: 25,
                              ),
                            ],
                          ),
                          child: Center(
                            child: _isLoading
                                ? const SizedBox(
                                    width: 25,
                                    height: 25,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 3,
                                      color: Colors.white,
                                    ),
                                  )
                                : Icon(
                                    _isPlaying
                                        ? Icons.pause
                                        : Icons.play_arrow,
                                    size: 32,
                                    color: Colors.white,
                                  ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 25),
                      Icon(
                        _volume == 0
                            ? Icons.volume_off
                            : Icons.volume_up,
                        color: const Color(0xFFCBD2E3),
                      ),
                      SizedBox(
                        width: 105,
                        child: Slider(
                          value: _volume,
                          min: 0,
                          max: 1,
                          onChanged: _changeVolume,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 28),
                  Text(
                    _isPlaying
                        ? "You're listening live"
                        : "Press play to start radio",
                    style: const TextStyle(
                      color: Color(0xFF707991),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
