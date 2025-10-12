"""
Sistema de gestión de audio para el juego.
Genera efectos de sonido sintéticos para la temática espacial.
"""
import pygame
import numpy as np
import math
import random
from typing import Dict, Optional
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class SoundManager:
    """Gestor de efectos de sonido sintéticos para el juego espacial."""
    
    def __init__(self):
        """Inicializa el sistema de audio."""
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        # Control de volumen
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.5
        
        # Control de habilitación de audio
        self.music_enabled = True
        self.sound_enabled = True
        
        # Cache de sonidos generados
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Generar todos los sonidos al inicializar
        self._generate_all_sounds()
        
        # Canal para música de fondo
        self.music_channel = pygame.mixer.Channel(0)
        self.ambient_playing = False
        
    def _generate_sine_wave(self, frequency: float, duration: float, 
                           sample_rate: int = 22050, amplitude: float = 0.3) -> np.ndarray:
        """
        Genera una onda senoidal.
        
        Args:
            frequency: Frecuencia en Hz
            duration: Duración en segundos
            sample_rate: Tasa de muestreo
            amplitude: Amplitud de la onda
            
        Returns:
            Array numpy con la onda generada
        """
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            wave = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            arr[i] = [wave, wave]
            
        return arr
        
    def _generate_noise(self, duration: float, sample_rate: int = 22050, 
                       amplitude: float = 0.2) -> np.ndarray:
        """
        Genera ruido blanco.
        
        Args:
            duration: Duración en segundos
            sample_rate: Tasa de muestreo  
            amplitude: Amplitud del ruido
            
        Returns:
            Array numpy con el ruido generado
        """
        frames = int(duration * sample_rate)
        arr = np.random.uniform(-amplitude, amplitude, (frames, 2))
        return arr
        
    def _apply_envelope(self, wave: np.ndarray, attack: float = 0.01, 
                       decay: float = 0.1, sustain: float = 0.7, 
                       release: float = 0.2) -> np.ndarray:
        """
        Aplica envolvente ADSR a una onda.
        
        Args:
            wave: Onda a procesar
            attack: Tiempo de ataque
            decay: Tiempo de decaimiento  
            sustain: Nivel de sostenimiento
            release: Tiempo de liberación
            
        Returns:
            Onda con envolvente aplicada
        """
        frames = len(wave)
        envelope = np.zeros(frames)
        
        # Calcular puntos de transición
        attack_frames = int(attack * 22050)
        decay_frames = int(decay * 22050) 
        release_start = frames - int(release * 22050)
        
        for i in range(frames):
            if i < attack_frames:
                # Fase de ataque
                envelope[i] = i / attack_frames
            elif i < attack_frames + decay_frames:
                # Fase de decaimiento
                progress = (i - attack_frames) / decay_frames
                envelope[i] = 1.0 - (1.0 - sustain) * progress
            elif i < release_start:
                # Fase de sostenimiento
                envelope[i] = sustain
            else:
                # Fase de liberación
                progress = (i - release_start) / (frames - release_start)
                envelope[i] = sustain * (1.0 - progress)
                
        # Aplicar envolvente
        wave[:, 0] *= envelope
        wave[:, 1] *= envelope
        
        return wave
        
    def _generate_laser_shot(self) -> pygame.mixer.Sound:
        """Genera sonido de disparo láser futurista."""
        duration = 0.25
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Frecuencia principal que desciende (efecto pew-pew)
        for i in range(frames):
            t = i / 22050
            # Frecuencia que baja de 1500Hz a 400Hz
            freq = 1500 - (1100 * t / duration)
            # Modulación de amplitud para efecto láser
            amp = 0.4 * (1.0 - t / duration) * math.sin(2 * math.pi * 8 * t)  # vibración
            wave = amp * math.sin(2 * math.pi * freq * t)
            combined[i] = [wave, wave]
            
        # Añadir armónicos para riqueza tonal
        for i in range(frames):
            t = i / 22050
            freq2 = 2400 - (1600 * t / duration)  # Harmónico superior
            amp2 = 0.15 * (1.0 - t / duration)
            wave2 = amp2 * math.sin(2 * math.pi * freq2 * t)
            combined[i] += [wave2, wave2]
            
        # Ruido blanco sutil para textura
        noise = self._generate_noise(duration, amplitude=0.05)
        combined[:len(noise)] += noise
        
        # Envolvente muy rápida para efecto "zap"
        combined = self._apply_envelope(combined, 0.005, 0.02, 0.3, 0.18)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
        
    def _generate_explosion(self) -> pygame.mixer.Sound:
        """Genera sonido de explosión."""
        # Ruido con bajas frecuencias
        noise = self._generate_noise(0.8, amplitude=0.4)
        low_freq = self._generate_sine_wave(60, 0.6, amplitude=0.3)
        mid_freq = self._generate_sine_wave(150, 0.4, amplitude=0.2)
        
        # Combinar
        max_len = max(len(noise), len(low_freq), len(mid_freq))
        combined = np.zeros((max_len, 2))
        
        combined[:len(noise)] += noise
        combined[:len(low_freq)] += low_freq
        combined[:len(mid_freq)] += mid_freq
        
        # Envolvente de explosión
        combined = self._apply_envelope(combined, 0.001, 0.1, 0.3, 0.5)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
        
    def _generate_damage_sound(self) -> pygame.mixer.Sound:
        """Genera sonido de daño recibido."""
        # Sonido agudo y corto
        wave = self._generate_sine_wave(400, 0.2, amplitude=0.3)
        noise = self._generate_noise(0.1, amplitude=0.15)
        
        combined = np.zeros((len(wave), 2))
        combined[:len(wave)] += wave
        combined[:len(noise)] += noise
        
        # Envolvente rápida y dramática
        combined = self._apply_envelope(combined, 0.005, 0.05, 0.4, 0.14)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
        
    def _generate_enemy_death(self) -> pygame.mixer.Sound:
        """Genera sonido de muerte de enemigo."""
        # Sonido descendente 
        frames = int(0.5 * 22050)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # Frecuencia que desciende
            freq = 600 - (400 * i / frames)
            wave = 0.25 * math.sin(2 * math.pi * freq * i / 22050)
            arr[i] = [wave, wave]
            
        # Añadir algo de ruido
        noise = self._generate_noise(0.3, amplitude=0.1)
        arr[:len(noise)] += noise
        
        arr = self._apply_envelope(arr, 0.01, 0.1, 0.5, 0.3)
        
        return pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
        
    def _generate_level_complete(self) -> pygame.mixer.Sound:
        """Genera sonido de nivel completado."""
        # Acorde ascendente
        freqs = [262, 330, 392, 523]  # Do, Mi, Sol, Do (octava)
        combined = np.zeros((int(1.0 * 22050), 2))
        
        for i, freq in enumerate(freqs):
            start = int(i * 0.2 * 22050)
            wave = self._generate_sine_wave(freq, 0.6, amplitude=0.2)
            end = min(len(combined), start + len(wave))
            combined[start:end] += wave[:end-start]
            
        combined = self._apply_envelope(combined, 0.05, 0.1, 0.7, 0.3)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
        
    def _generate_ambient_space(self) -> pygame.mixer.Sound:
        """Genera ambiente espacial de fondo."""
        # Sonido largo y sutil para loop
        duration = 10.0  # 10 segundos
        frames = int(duration * 22050)
        arr = np.zeros((frames, 2))
        
        # Múltiples ondas de baja frecuencia
        for freq in [40, 60, 80, 120]:
            for i in range(frames):
                # Variación sutil en amplitud
                amp = 0.05 + 0.02 * math.sin(2 * math.pi * 0.1 * i / 22050)
                wave = amp * math.sin(2 * math.pi * freq * i / 22050)
                arr[i] += [wave, wave]
                
        # Añadir ruido muy suave
        noise = self._generate_noise(duration, amplitude=0.03)
        arr += noise
        
        return pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
        
    def _generate_level_victory(self) -> pygame.mixer.Sound:
        """Genera sonido de victoria de nivel (diferente al de completar todo el juego)."""
        # Fanfare corta y enérgica
        duration = 1.5
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Secuencia de notas ascendentes (Do-Mi-Sol-Do-Mi)
        notes = [262, 330, 392, 523, 659]  # Frecuencias en Hz
        note_duration = duration / len(notes)
        
        for i, freq in enumerate(notes):
            start_frame = int(i * note_duration * 22050)
            note_frames = int(note_duration * 22050)
            
            # Generar nota con armónicos
            for frame in range(note_frames):
                if start_frame + frame >= frames:
                    break
                    
                t = frame / 22050
                # Nota fundamental
                wave = 0.3 * math.sin(2 * math.pi * freq * t)
                # Armónico (octava)
                wave += 0.15 * math.sin(2 * math.pi * freq * 2 * t)
                # Armónico (quinta)
                wave += 0.1 * math.sin(2 * math.pi * freq * 1.5 * t)
                
                # Envolvente de nota individual
                if frame < note_frames * 0.1:  # Attack
                    envelope = frame / (note_frames * 0.1)
                elif frame > note_frames * 0.7:  # Release
                    envelope = 1.0 - (frame - note_frames * 0.7) / (note_frames * 0.3)
                else:  # Sustain
                    envelope = 1.0
                    
                wave *= envelope
                combined[start_frame + frame] += [wave, wave]
                
        # Aplicar envolvente general
        combined = self._apply_envelope(combined, 0.05, 0.1, 0.8, 0.3)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
        
    def _generate_super_shot(self) -> pygame.mixer.Sound:
        """Genera sonido de super disparo (más potente y dramático)."""
        duration = 0.8
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Sonido base más grave y poderoso
        for i in range(frames):
            t = i / 22050
            # Frecuencias múltiples para efecto épico
            freq1 = 200 - (50 * t / duration)  # Grave profundo
            freq2 = 800 - (300 * t / duration)  # Media
            freq3 = 1600 - (800 * t / duration)  # Aguda
            
            # Modulación de amplitud dramática
            amp1 = 0.4 * (1.0 - t / duration) * math.sin(2 * math.pi * 15 * t)
            amp2 = 0.3 * (1.0 - t / duration) * math.sin(2 * math.pi * 10 * t)
            amp3 = 0.2 * (1.0 - t / duration)
            
            wave = amp1 * math.sin(2 * math.pi * freq1 * t)
            wave += amp2 * math.sin(2 * math.pi * freq2 * t)
            wave += amp3 * math.sin(2 * math.pi * freq3 * t)
            
            combined[i] = [wave, wave]
            
        # Ruido para textura
        noise = self._generate_noise(duration, amplitude=0.15)
        combined[:len(noise)] += noise
        
        # Envolvente dramática
        combined = self._apply_envelope(combined, 0.02, 0.1, 0.7, 0.4)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
        
    def _generate_character_select(self) -> pygame.mixer.Sound:
        """Genera sonido de selección de personaje."""
        # Sonido suave y futurista
        duration = 0.3
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / 22050
            # Dos frecuencias armónicas
            freq1 = 440  # La
            freq2 = 660  # Mi (quinta perfecta)
            
            amp = 0.2 * (1.0 - t / duration)
            wave = amp * math.sin(2 * math.pi * freq1 * t)
            wave += amp * 0.5 * math.sin(2 * math.pi * freq2 * t)
            
            combined[i] = [wave, wave]
            
        combined = self._apply_envelope(combined, 0.05, 0.1, 0.6, 0.15)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_pickup(self) -> pygame.mixer.Sound:
        """Genera sonido de recolección de objetos - alegre y positivo."""
        duration = 0.4
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / 22050
            # Secuencia ascendente de notas
            progress = t / duration
            
            if progress < 0.33:
                freq = 523  # Do5
            elif progress < 0.66:
                freq = 659  # Mi5
            else:
                freq = 784  # Sol5
            
            # Amplitud que decrece suavemente
            amp = 0.25 * (1.0 - progress * 0.5)
            
            # Onda principal con armónicos
            wave = amp * math.sin(2 * math.pi * freq * t)
            wave += amp * 0.3 * math.sin(2 * math.pi * freq * 2 * t)  # Octava
            wave += amp * 0.15 * math.sin(2 * math.pi * freq * 3 * t)  # Quinta
            
            # Pequeña reverberación
            if i > 1000:
                wave += 0.1 * combined[i-1000][0]
            
            combined[i] = [wave, wave]
            
        combined = self._apply_envelope(combined, 0.02, 0.05, 0.8, 0.15)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_coin_pickup(self) -> pygame.mixer.Sound:
        """Genera sonido de recolección de monedas - brillante y satisfactorio."""
        duration = 0.5
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / 22050
            progress = t / duration
            
            # Secuencia de notas que suben (Do-Mi-Sol-Do octava)
            if progress < 0.2:
                freq = 523  # Do5
            elif progress < 0.4:
                freq = 659  # Mi5
            elif progress < 0.7:
                freq = 784  # Sol5
            else:
                freq = 1047  # Do6 (octava)
            
            # Amplitud que decrece gradualmente
            amp = 0.3 * (1.0 - progress * 0.7)
            
            # Onda principal con armónicos dorados
            wave = amp * math.sin(2 * math.pi * freq * t)
            wave += amp * 0.4 * math.sin(2 * math.pi * freq * 2 * t)  # Octava
            wave += amp * 0.2 * math.sin(2 * math.pi * freq * 4 * t)  # Cuarta octava
            
            # Efecto de tintineo
            tinkle = 0.1 * amp * math.sin(2 * math.pi * freq * 8 * t) * math.exp(-t * 5)
            wave += tinkle
            
            # Reverb ligero
            if i > 500:
                wave += 0.15 * combined[i-500][0]
                
            combined[i] = [wave, wave]
            
        combined = self._apply_envelope(combined, 0.01, 0.03, 0.9, 0.2)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_powerup_pickup(self) -> pygame.mixer.Sound:
        """Genera sonido de recolección de power-ups - épico y poderoso."""
        duration = 0.8
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / 22050
            progress = t / duration
            
            # Acordes ascendentes potentes
            if progress < 0.3:
                freqs = [220, 277, 330]  # Acorde Am
            elif progress < 0.6:
                freqs = [261, 329, 392]  # Acorde C
            else:
                freqs = [349, 440, 523]  # Acorde F
            
            # Amplitud con pico en el medio
            amp = 0.25 * math.sin(math.pi * progress)
            
            wave = 0
            for j, freq in enumerate(freqs):
                # Cada nota con diferente peso
                note_amp = amp * (0.8 if j == 0 else 0.6 if j == 1 else 0.4)
                wave += note_amp * math.sin(2 * math.pi * freq * t)
                
            # Efecto de energía creciente
            energy = 0.15 * math.sin(2 * math.pi * 1000 * t) * progress
            wave += energy
            
            # Reverb espacial
            if i > 1000:
                wave += 0.2 * combined[i-1000][0]
                
            combined[i] = [wave, wave]
            
        combined = self._apply_envelope(combined, 0.05, 0.1, 0.7, 0.3)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_level_up(self) -> pygame.mixer.Sound:
        """Genera sonido de subida de nivel - triunfante y épico."""
        duration = 1.5
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / 22050
            progress = t / duration
            
            # Progresión triunfante: Do-Fa-Sol-Do octava
            if progress < 0.25:
                base_freq = 261  # Do4
            elif progress < 0.5:
                base_freq = 349  # Fa4
            elif progress < 0.75:
                base_freq = 392  # Sol4
            else:
                base_freq = 523  # Do5
            
            # Amplitud que crece y luego decrece
            if progress < 0.8:
                amp = 0.3 * (progress / 0.8)
            else:
                amp = 0.3 * (1.0 - (progress - 0.8) / 0.2)
            
            # Onda principal con armónicos ricos
            wave = amp * math.sin(2 * math.pi * base_freq * t)
            wave += amp * 0.6 * math.sin(2 * math.pi * base_freq * 2 * t)  # Octava
            wave += amp * 0.3 * math.sin(2 * math.pi * base_freq * 3 * t)  # Quinta
            
            # Coro de fondo (quinta perfecta)
            harmony_freq = base_freq * 1.5  # Quinta perfecta
            wave += amp * 0.4 * math.sin(2 * math.pi * harmony_freq * t)
            
            # Efectos de brillo
            sparkle = 0.1 * amp * math.sin(2 * math.pi * base_freq * 4 * t) * math.sin(t * 8)
            wave += sparkle
            
            # Reverb épico
            if i > 2000:
                wave += 0.25 * combined[i-2000][0]
                
            combined[i] = [wave, wave]
            
        combined = self._apply_envelope(combined, 0.1, 0.2, 0.6, 0.4)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_background_ambient(self) -> pygame.mixer.Sound:
        """Genera música de fondo ambiental para el juego."""
        duration = 30.0  # 30 segundos de loop
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        for i in range(frames):
            t = i / 22050
            
            # Base rítmica suave
            bass_freq = 55  # La grave
            bass_wave = 0.15 * math.sin(2 * math.pi * bass_freq * t)
            bass_wave += 0.1 * math.sin(2 * math.pi * bass_freq * 2 * t)
            
            # Pad atmosférico
            pad_freq1 = 220 * (1 + 0.05 * math.sin(2 * math.pi * 0.1 * t))  # Modulación lenta
            pad_freq2 = 330 * (1 + 0.03 * math.sin(2 * math.pi * 0.07 * t))
            
            pad_wave = 0.08 * math.sin(2 * math.pi * pad_freq1 * t)
            pad_wave += 0.06 * math.sin(2 * math.pi * pad_freq2 * t)
            
            # Efectos espaciales esporádicos
            if random.random() < 0.001:  # Muy ocasional
                space_freq = random.uniform(800, 1200)
                space_effect = 0.05 * math.sin(2 * math.pi * space_freq * t) * math.exp(-t * 0.5)
                pad_wave += space_effect
            
            # Combinar todo
            wave = bass_wave + pad_wave
            
            # Filtro suave para evitar harshness
            if i > 0:
                wave = 0.7 * wave + 0.3 * combined[i-1][0]
                
            combined[i] = [wave, wave]
            
        # Aplicar fade in/out para loop seamless
        fade_frames = 22050  # 1 segundo
        for i in range(fade_frames):
            fade_mult = i / fade_frames
            combined[i] *= fade_mult
            combined[-(i+1)] *= fade_mult
            
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_boss_laser(self) -> pygame.mixer.Sound:
        """Genera sonido de láser de boss - intenso y amenazante."""
        duration = 1.2
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Frecuencias bajas y potentes para el láser del boss
        for i in range(frames):
            t = i / 22050
            # Múltiples frecuencias superpuestas
            freq1 = 80 * (1 + 0.2 * math.sin(2 * math.pi * 5 * t))  # Modulación
            freq2 = 120 * (1 + 0.15 * math.sin(2 * math.pi * 3 * t))
            freq3 = 200 * (1 + 0.1 * math.sin(2 * math.pi * 7 * t))
            
            # Amplitudes que decaen
            amp1 = 0.4 * (1.0 - 0.3 * t / duration)
            amp2 = 0.3 * (1.0 - 0.2 * t / duration)  
            amp3 = 0.2 * (1.0 - 0.1 * t / duration)
            
            wave = (amp1 * math.sin(2 * math.pi * freq1 * t) +
                    amp2 * math.sin(2 * math.pi * freq2 * t) +
                    amp3 * math.sin(2 * math.pi * freq3 * t))
            
            # Agregar algo de ruido
            noise_val = random.uniform(-0.1, 0.1)
            wave += noise_val
            
            combined[i] = [wave, wave]
        
        # Envolvente con ataque rápido y decaimiento gradual
        combined = self._apply_envelope(combined, 0.05, 0.2, 0.6, 0.4)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_boss_defeat(self) -> pygame.mixer.Sound:
        """Genera sonido épico de derrota de boss."""
        duration = 2.5
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Secuencia descendente dramática
        frequencies = [400, 300, 200, 150, 100, 80, 60]
        segment_frames = frames // len(frequencies)
        
        for seg_idx, freq in enumerate(frequencies):
            start_frame = seg_idx * segment_frames
            end_frame = min(start_frame + segment_frames, frames)
            
            for i in range(start_frame, end_frame):
                t = i / 22050
                local_t = (i - start_frame) / (end_frame - start_frame)
                
                # Frecuencia que baja gradualmente dentro del segmento
                current_freq = freq * (1.0 - 0.3 * local_t)
                
                # Amplitud que decae con el tiempo total
                amp = 0.5 * (1.0 - 0.7 * t / duration)
                
                # Onda principal
                wave = amp * math.sin(2 * math.pi * current_freq * t)
                
                # Agregar algo de ruido para dramatismo
                noise_val = random.uniform(-0.1, 0.1) * amp
                wave += noise_val
                
                combined[i] = [wave, wave]
        
        # Envolvente dramática con decaimiento largo
        combined = self._apply_envelope(combined, 0.1, 0.5, 0.3, 1.0)
        
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_menu_music(self) -> pygame.mixer.Sound:
        """Genera música épica para el menú principal."""
        duration = 12.0  # 12 segundos de loop
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Melodía principal épica
        melody_notes = [
            (220, 1.0), (247, 0.5), (262, 0.5), (294, 1.0),  # A4, B4, C5, D5
            (330, 1.5), (294, 0.5), (262, 1.0), (247, 1.0),  # E5, D5, C5, B4
            (220, 2.0), (196, 1.0), (220, 1.0), (262, 2.0)   # A4, G4, A4, C5
        ]
        
        current_frame = 0
        for freq, note_duration in melody_notes:
            note_frames = int(note_duration * 22050)
            end_frame = min(current_frame + note_frames, frames)
            
            for i in range(current_frame, end_frame):
                t = (i - current_frame) / 22050
                # Melodía principal
                melody = 0.3 * math.sin(2 * math.pi * freq * t)
                # Armonía (quinta)
                harmony = 0.15 * math.sin(2 * math.pi * freq * 1.5 * t)
                # Base (octava baja)
                bass = 0.2 * math.sin(2 * math.pi * freq * 0.5 * t)
                
                wave = melody + harmony + bass
                combined[i] = [wave, wave]
            
            current_frame = end_frame
            if current_frame >= frames:
                break
        
        # Envolvente suave
        combined = self._apply_envelope(combined, 0.5, 1.0, 0.8, 2.0)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_level_music(self) -> pygame.mixer.Sound:
        """Genera música de acción para los niveles."""
        duration = 8.0  # 8 segundos de loop
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Ritmo de batalla rápido
        beat_freq = 2.0  # 2 beats por segundo
        for i in range(frames):
            t = i / 22050
            
            # Línea de bajo pulsante
            bass_beat = math.sin(2 * math.pi * beat_freq * t)
            bass = 0.25 * math.sin(2 * math.pi * 80 * t) * (0.8 + 0.2 * bass_beat)
            
            # Melodía agresiva
            melody_freq = 440 + 50 * math.sin(2 * math.pi * 0.25 * t)  # Modulación
            melody = 0.2 * math.sin(2 * math.pi * melody_freq * t)
            
            # Percusión sintética
            percussion = 0.15 * random.uniform(-1, 1) * (1 if int(t * 4) % 2 == 0 else 0.3)
            
            wave = bass + melody + percussion
            combined[i] = [wave, wave]
        
        # Envolvente de combate
        combined = self._apply_envelope(combined, 0.1, 0.2, 0.9, 0.1)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_leaderboard_music(self) -> pygame.mixer.Sound:
        """Genera música tranquila para la pantalla de puntuaciones."""
        duration = 10.0  # 10 segundos de loop
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Melodía suave y relajante
        peaceful_notes = [330, 294, 262, 294, 330, 370, 330, 294]  # Pentatónica
        
        for i in range(frames):
            t = i / 22050
            
            # Nota principal que cambia suavemente
            note_index = int(t * 0.8) % len(peaceful_notes)
            main_freq = peaceful_notes[note_index]
            
            # Melodía principal suave
            main = 0.2 * math.sin(2 * math.pi * main_freq * t)
            
            # Armonía etérea
            harmony = 0.1 * math.sin(2 * math.pi * main_freq * 1.25 * t)
            
            # Pad atmosférico
            pad = 0.05 * math.sin(2 * math.pi * main_freq * 0.5 * t)
            
            wave = main + harmony + pad
            combined[i] = [wave, wave]
        
        # Envolvente muy suave
        combined = self._apply_envelope(combined, 1.0, 2.0, 0.6, 2.0)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_death_music(self) -> pygame.mixer.Sound:
        """Genera música melancólica para el game over."""
        duration = 8.0  # 8 segundos de loop
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Progresión menor triste
        death_notes = [196, 175, 155, 147, 131, 117, 110, 98]  # Escala descendente menor
        
        for i in range(frames):
            t = i / 22050
            
            # Nota principal descendente lentamente
            note_index = int(t * 0.5) % len(death_notes)
            main_freq = death_notes[note_index]
            
            # Melodía principal melancólica
            main = 0.3 * math.sin(2 * math.pi * main_freq * t) * (1 - t * 0.1)
            
            # Armonía grave y sombría
            harmony = 0.15 * math.sin(2 * math.pi * main_freq * 0.75 * t)
            
            # Reverb ambiente
            reverb = 0.05 * math.sin(2 * math.pi * main_freq * 0.25 * t)
            
            # Añadir algo de distorsión sutil para tristeza
            distortion = 0.02 * math.sin(2 * math.pi * main_freq * 3 * t) * math.sin(t * 2)
            
            wave = main + harmony + reverb + distortion
            combined[i] = [wave, wave]
        
        # Envolvente con fade out gradual
        combined = self._apply_envelope(combined, 0.5, 1.0, 0.4, 3.0)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
    
    def _generate_victory_music(self) -> pygame.mixer.Sound:
        """Genera música épica de victoria total."""
        duration = 6.0  # 6 segundos de fanfare triunfal
        frames = int(duration * 22050)
        combined = np.zeros((frames, 2))
        
        # Progresión triunfal ascendente - Do Mayor heroico
        victory_notes = [262, 294, 330, 349, 392, 440, 494, 523, 587, 659]  # Do a Mi alto
        
        for i in range(frames):
            t = i / 22050
            phase = t / duration  # 0 a 1 durante la duración
            
            # Melodía principal que asciende heroicamente
            note_index = min(len(victory_notes) - 1, int(phase * len(victory_notes)))
            main_freq = victory_notes[note_index]
            
            # Melodía principal potente
            main = 0.4 * math.sin(2 * math.pi * main_freq * t)
            
            # Armonía en octavas para magnificencia
            harmony_high = 0.2 * math.sin(2 * math.pi * main_freq * 2 * t)
            harmony_low = 0.15 * math.sin(2 * math.pi * main_freq * 0.5 * t)
            
            # Acordes triunfales (tercera y quinta)
            chord_third = 0.1 * math.sin(2 * math.pi * main_freq * 1.25 * t)
            chord_fifth = 0.1 * math.sin(2 * math.pi * main_freq * 1.5 * t)
            
            # Trompetas ceremoniales (ligera distorsión armónica)
            trumpet = 0.08 * math.sin(2 * math.pi * main_freq * 3 * t) * math.sin(t * 0.5)
            
            # Crescendo épico
            crescendo = min(1.0, t * 2.0)  # Aumenta volumen durante la primera mitad
            
            wave = (main + harmony_high + harmony_low + chord_third + chord_fifth + trumpet) * crescendo
            combined[i] = [wave, wave]
        
        # Envolvente épica con ataque rápido y final brillante
        combined = self._apply_envelope(combined, 0.1, 0.2, 0.6, 0.8)
        return pygame.sndarray.make_sound((combined * 32767).astype(np.int16))
        
    def _generate_all_sounds(self) -> None:
        """Genera todos los efectos de sonido."""
        print("Generando efectos de sonido...")
        
        self.sounds['laser_shot'] = self._generate_laser_shot()
        self.sounds['explosion'] = self._generate_explosion()  
        self.sounds['damage'] = self._generate_damage_sound()
        self.sounds['enemy_death'] = self._generate_enemy_death()
        self.sounds['level_complete'] = self._generate_level_complete()
        self.sounds['level_victory'] = self._generate_level_victory()
        self.sounds['super_shot'] = self._generate_super_shot()
        self.sounds['character_select'] = self._generate_character_select()
        self.sounds['pickup'] = self._generate_pickup()
        self.sounds['coin_pickup'] = self._generate_coin_pickup()
        self.sounds['powerup_pickup'] = self._generate_powerup_pickup()
        self.sounds['level_up'] = self._generate_level_up()
        self.sounds['background_ambient'] = self._generate_background_ambient()
        self.sounds['boss_laser'] = self._generate_boss_laser()
        self.sounds['boss_defeat'] = self._generate_boss_defeat()
        self.sounds['ambient_space'] = self._generate_ambient_space()
        
        # Música de fondo
        print("Generando música de fondo...")
        self.sounds['menu_music'] = self._generate_menu_music()
        self.sounds['level_music'] = self._generate_level_music()
        self.sounds['leaderboard_music'] = self._generate_leaderboard_music()
        self.sounds['death_music'] = self._generate_death_music()
        self.sounds['victory_music'] = self._generate_victory_music()
        
        print("Efectos de sonido y música generados correctamente.")
        
    def play_sound(self, sound_name: str, volume: Optional[float] = None) -> None:
        """
        Reproduce un efecto de sonido.
        
        Args:
            sound_name: Nombre del sonido a reproducir
            volume: Volumen específico (opcional)
        """
        if not self.sound_enabled:
            return
            
        if sound_name not in self.sounds:
            print(f"Sonido '{sound_name}' no encontrado")
            return
            
        sound = self.sounds[sound_name]
        
        # Configurar volumen
        final_volume = (volume or self.sfx_volume) * self.master_volume
        sound.set_volume(final_volume)
        
        # Reproducir
        sound.play()
        
    def start_ambient_music(self) -> None:
        """Inicia la música ambiental de fondo."""
        if not self.ambient_playing:
            ambient = self.sounds['ambient_space']
            ambient.set_volume(self.music_volume * self.master_volume)
            self.music_channel.play(ambient, loops=-1)  # Loop infinito
            self.ambient_playing = True
            
    def stop_ambient_music(self) -> None:
        """Detiene la música ambiental."""
        self.music_channel.stop()
        self.ambient_playing = False
        
    def set_master_volume(self, volume: float) -> None:
        """
        Establece el volumen maestro.
        
        Args:
            volume: Volumen entre 0.0 y 1.0
        """
        self.master_volume = max(0.0, min(1.0, volume))
        
        # Actualizar volumen de música ambiental si está sonando
        if self.ambient_playing:
            ambient = self.sounds['ambient_space']
            ambient.set_volume(self.music_volume * self.master_volume)
    
    def play_menu_music(self) -> None:
        """Reproduce la música del menú en loop."""
        if not self.music_enabled:
            return
            
        if 'menu_music' in self.sounds:
            self.stop_ambient_music()
            music = self.sounds['menu_music']
            music.set_volume(self.music_volume * self.master_volume)
            self.music_channel.play(music, loops=-1)
            self.ambient_playing = True
    
    def play_level_music(self) -> None:
        """Reproduce la música de nivel en loop."""
        if not self.music_enabled:
            return
            
        if 'level_music' in self.sounds:
            self.stop_ambient_music()
            music = self.sounds['level_music']
            music.set_volume(self.music_volume * self.master_volume)
            self.music_channel.play(music, loops=-1)
            self.ambient_playing = True
    
    def play_leaderboard_music(self) -> None:
        """Reproduce la música de puntuaciones en loop."""
        if 'leaderboard_music' in self.sounds:
            self.stop_ambient_music()
            music = self.sounds['leaderboard_music']
            music.set_volume(self.music_volume * self.master_volume)
            self.music_channel.play(music, loops=-1)
            self.ambient_playing = True
    
    def play_death_music(self) -> None:
        """Reproduce la música de muerte/game over en loop."""
        if 'death_music' in self.sounds:
            self.stop_ambient_music()
            music = self.sounds['death_music']
            music.set_volume(self.music_volume * self.master_volume)
            self.music_channel.play(music, loops=-1)
            self.ambient_playing = True
    
    def play_victory_music(self) -> None:
        """Reproduce la música de victoria total (una sola vez)."""
        if not self.music_enabled:
            return
            
        if 'victory_music' in self.sounds:
            self.stop_ambient_music()
            music = self.sounds['victory_music']
            music.set_volume(self.music_volume * self.master_volume)
            self.music_channel.play(music, loops=0)  # Sin loop, una sola vez
            self.ambient_playing = True