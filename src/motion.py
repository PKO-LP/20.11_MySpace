import math


def orbit_position(radius, angle):
    radians = math.radians(angle)
    return radius * math.cos(radians), 0, radius * math.sin(radians)


def next_angle(angle, speed, delta, multiplier, paused):
    if paused:
        return angle
    return (angle + speed * delta * multiplier) % 360


def zoom_distance(distance, direction, minimum, maximum):
    return max(minimum, min(maximum, distance * (0.85 ** direction)))
