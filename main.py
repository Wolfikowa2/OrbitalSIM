import pygame
import math
import sys
import random
import asyncio

pygame.init()

WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Quantum Simulator - Tvary a Kontext")
clock = pygame.time.Clock()

# Zde je ta klicova oprava pro web: pouzivame zabudovany font (None)
font_tiny = pygame.font.Font(None, 16)
font_small = pygame.font.Font(None, 20)
font_medium = pygame.font.Font(None, 26)
font_large = pygame.font.Font(None, 36)
font_title = pygame.font.Font(None, 46)
font_huge = pygame.font.Font(None, 66)

BG_COLOR = (10, 12, 15)
WHITE = (255, 255, 255)
GRAY = (150, 150, 160)

COLOR_SP_POS = (100, 255, 120)
COLOR_SP_NEG = (255, 100, 255)
COLOR_D_POS = (255, 150, 50)
COLOR_D_NEG = (50, 200, 255)

def eval_psi(otype, x, y, z, r):
    if r == 0: return 0
    decay = math.exp(-r / 1.8) 
    
    if otype == '1s':
        return math.exp(-r / 1.2)
    elif otype == '2pz':
        return z * decay
    elif otype == 'sp3':
        return (1.0 + 2.5 * z) * math.exp(-r / 1.6)
    elif otype == 'dxy':
        return x * y * decay
    elif otype == 'dxz':
        return x * z * decay
    elif otype == 'dyz':
        return y * z * decay
    elif otype == 'dx2-y2':
        return (x*x - y*y) * decay
    elif otype == 'dz2':
        return (2*z*z - x*x - y*y) * decay
    return 0

def generate_electron_cloud(otype, is_d_orbital, num_points=4000):
    points = []
    max_p = 0.0
    
    for _ in range(6000):
        x, y, z = random.uniform(-6, 6), random.uniform(-6, 6), random.uniform(-6, 6)
        r = math.sqrt(x*x + y*y + z*z)
        psi = eval_psi(otype, x, y, z, r)
        if psi**2 > max_p: max_p = psi**2

    while len(points) < num_points:
        x, y, z = random.uniform(-7, 7), random.uniform(-7, 7), random.uniform(-7, 7)
        r = math.sqrt(x*x + y*y + z*z)
        psi = eval_psi(otype, x, y, z, r)
        prob = psi**2
        
        if random.random() * max_p < (prob * 1.2): 
            is_positive_phase = (psi > 0)
            if is_d_orbital:
                color = COLOR_D_POS if is_positive_phase else COLOR_D_NEG
            else:
                color = COLOR_SP_POS if is_positive_phase else COLOR_SP_NEG
                
            points.append([x*35, y*35, z*35, color])
            
    return points

def rotate_3d(x, y, z, angle_x, angle_y):
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y1 = y * cos_x - z * sin_x
    z1 = y * sin_x + z * cos_x
    
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x2 = x * cos_y + z1 * sin_y
    z2 = -x * sin_y + z1 * cos_y
    return x2, y1, z2

def create_glow_sprite(color, radius):
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    r, g, b = color
    pygame.draw.circle(surf, (r, g, b, 20), (radius, radius), radius)
    pygame.draw.circle(surf, (r, g, b, 80), (radius, radius), radius*0.6)
    pygame.draw.circle(surf, (255, 255, 255, 200), (radius, radius), radius*0.2)
    return surf

ORBITALS = [
    {'id': '1s', 'name': '1s Orbital', 'type': 'sp', 'desc': 'Koule. Nema zadny uzel. Elektron obaluje jadro ze vsech stran rovnomerne.'},
    {'id': '2pz', 'name': '2p_z Orbital', 'type': 'sp', 'desc': 'Tvar cinky. Uzel v rovine XY rozdeluje elektronovou hustotu na dve poloviny opacne faze.'},
    {'id': 'sp3', 'name': 'sp3 Hybrid', 'type': 'sp', 'desc': 'Kdyz atom uhliku tvori vazby, smicha s a p orbitaly. Velky lalok ukazuje presne na misto, kde se pripoji dalsi atom.'},
    {'id': 'dxy', 'name': 'd_xy', 'type': 'd', 'desc': 'Laloky mieri MEZI ligandy (okolni atomy). Diky tomu d_xy netrpi tak velkym odpuzovanim elektronu od okolnich atomu.'},
    {'id': 'dxz', 'name': 'd_xz', 'type': 'd', 'desc': 'Podobne jako d_xy, elektronova hustota proteka bezpecne mezi osami X a Z, mimo prime chemicke vazby.'},
    {'id': 'dyz', 'name': 'd_yz', 'type': 'd', 'desc': 'Treti orbital, ktery se vyhyba osam. Lezi presne mezi osou Y a Z.'},
    {'id': 'dx2-y2', 'name': 'd_x2-y2', 'type': 'd', 'desc': 'Tento orbital mieri PRIMO na ligandy lezici na osach X a Y. Proto ma v chemickych komplexech obvykle vyssi energii.'},
    {'id': 'dz2', 'name': 'd_z2', 'type': 'd', 'desc': 'Mieri PRIMO na ligandy na ose Z. Toroidni prstenec stabilizuje elektronovou hustotu v rovine XY.'}
]

async def main():
    clouds = {}
    
    for i, orb in enumerate(ORBITALS):
        screen.fill(BG_COLOR)
        loading_txt = font_huge.render("Pocitam kvantove modely...", True, WHITE)
        screen.blit(loading_txt, (WIDTH//2 - loading_txt.get_width()//2, HEIGHT//2 - 50))
        
        progress_txt = f"Generuji tvar: {orb['name']} ({i+1}/{len(ORBITALS)})"
        sub_txt = font_medium.render(progress_txt, True, GRAY)
        screen.blit(sub_txt, (WIDTH//2 - sub_txt.get_width()//2, HEIGHT//2 + 30))
        
        pygame.draw.rect(screen, (50, 50, 60), (WIDTH//2 - 200, HEIGHT//2 + 80, 400, 10))
        pygame.draw.rect(screen, COLOR_SP_POS, (WIDTH//2 - 200, HEIGHT//2 + 80, int(400 * ((i+1)/len(ORBITALS))), 10))
        
        pygame.display.flip()
        
        is_d = (orb['type'] == 'd')
        clouds[orb['id']] = generate_electron_cloud(orb['id'], is_d, 4000)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        await asyncio.sleep(0)

    sprites = {
        COLOR_SP_POS: create_glow_sprite(COLOR_SP_POS, 4),
        COLOR_SP_NEG: create_glow_sprite(COLOR_SP_NEG, 4),
        COLOR_D_POS: create_glow_sprite(COLOR_D_POS, 4),
        COLOR_D_NEG: create_glow_sprite(COLOR_D_NEG, 4)
    }

    current_idx = 0
    rot_x, rot_y = 0.5, 0.5
    is_dragging = False
    show_context = False
    
    btn_w = 140
    buttons = []
    start_x1 = (int(WIDTH * 0.65) - (3 * btn_w + 40)) // 2
    for i in range(3):
        buttons.append(pygame.Rect(start_x1 + i*(btn_w + 20), HEIGHT - 130, btn_w, 40))
        
    start_x2 = (int(WIDTH * 0.65) - (5 * btn_w + 80)) // 2
    for i in range(3, 8):
        buttons.append(pygame.Rect(start_x2 + (i-3)*(btn_w + 20), HEIGHT - 70, btn_w, 40))

    btn_context = pygame.Rect(40, 40, 320, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    
                    if btn_context.collidepoint(mx, my):
                        show_context = not show_context
                        continue
                    
                    clicked_btn = False
                    for i, btn in enumerate(buttons):
                        if btn.collidepoint(mx, my):
                            current_idx = i
                            clicked_btn = True
                            break
                    if not clicked_btn:
                        is_dragging = True
                        pygame.mouse.get_rel()
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: is_dragging = False
                
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx, dy = event.rel
                    rot_y += dx * 0.01
                    rot_x -= dy * 0.01

        if not is_dragging:
            rot_y += 0.003

        screen.fill(BG_COLOR)

        current_data = ORBITALS[current_idx]
        cloud = clouds[current_data['id']]
        
        render_queue = []
        cx = WIDTH * 0.33
        cy = HEIGHT // 2

        axes = [
            {'end': (200, 0, 0), 'color': (150, 40, 40), 'label': 'X'},
            {'end': (0, 200, 0), 'color': (40, 150, 40), 'label': 'Y'},
            {'end': (0, 0, 200), 'color': (40, 100, 150), 'label': 'Z'}
        ]
        
        for ax in axes:
            rx, ry, rz = rotate_3d(*ax['end'], rot_x, rot_y)
            sx = rx + cx
            sy = -ry + cy
            render_queue.append({'type': 'axis', 'sx1': cx, 'sy1': cy, 'sx2': sx, 'sy2': sy, 'z': rz, 'c': ax['color'], 'l': ax['label']})

        if show_context:
            context_points = []
            if current_data['type'] == 'd':
                L = 180
                context_points = [(L,0,0), (-L,0,0), (0,L,0), (0,-L,0), (0,0,L), (0,0,-L)]
            elif current_data['id'] == 'sp3':
                L = 120
                context_points = [(L,L,L), (L,-L,-L), (-L,L,-L), (-L,-L,L)]
            elif current_data['id'] == '2pz':
                L = 150
                context_points = [(0,0,L), (0,0,-L)]

            for p in context_points:
                rx, ry, rz = rotate_3d(*p, rot_x, rot_y)
                sx = rx + cx
                sy = -ry + cy
                render_queue.append({'type': 'bond', 'sx1': cx, 'sy1': cy, 'sx2': sx, 'sy2': sy, 'z': rz})
                render_queue.append({'type': 'ligand', 'sx': sx, 'sy': sy, 'z': rz})

        for pt in cloud:
            jx = pt[0] + random.uniform(-1.5, 1.5)
            jy = pt[1] + random.uniform(-1.5, 1.5)
            jz = pt[2] + random.uniform(-1.5, 1.5)
            
            rx, ry, rz = rotate_3d(jx, jy, jz, rot_x, rot_y)
            sx = rx + cx
            sy = -ry + cy
            render_queue.append({'type': 'orb', 'sx': sx, 'sy': sy, 'z': rz, 'color': pt[3]})

        render_queue.sort(key=lambda item: item['z'], reverse=True)

        for item in render_queue:
            if item['type'] == 'axis':
                pygame.draw.line(screen, item['c'], (item['sx1'], item['sy1']), (item['sx2'], item['sy2']), 2)
                lbl = font_large.render(item['l'], True, item['c'])
                screen.blit(lbl, (item['sx2'] + 5, item['sy2'] - 10))
            elif item['type'] == 'bond':
                pygame.draw.line(screen, (200, 200, 200), (item['sx1'], item['sy1']), (item['sx2'], item['sy2']), 4)
            elif item['type'] == 'ligand':
                pygame.draw.circle(screen, (50, 50, 60), (int(item['sx']), int(item['sy'])), 16)
                pygame.draw.circle(screen, (200, 200, 200), (int(item['sx']), int(item['sy'])), 14)
        
        for item in render_queue:
            if item['type'] == 'orb':
                alpha = max(50, min(255, 255 - int((item['z'] + 100) * 0.8)))
                sprite = sprites[item['color']].copy()
                sprite.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(sprite, (int(item['sx'])-4, int(item['sy'])-4), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.circle(screen, WHITE, (int(cx), int(cy)), 8)

        ctx_color = (80, 150, 80) if show_context else (60, 60, 70)
        pygame.draw.rect(screen, ctx_color, btn_context, border_radius=8)
        ctx_txt = font_medium.render("Vypnout atomovy kontext" if show_context else "Zobrazit atomovy kontext (Vazby)", True, WHITE)
        screen.blit(ctx_txt, (btn_context.x + 20, btn_context.y + 12))

        panel_x = int(WIDTH * 0.65)
        pygame.draw.rect(screen, (20, 24, 30), (panel_x, 0, WIDTH - panel_x, HEIGHT))
        pygame.draw.line(screen, (70, 80, 100), (panel_x, 0), (panel_x, HEIGHT), 3)

        y_pos = 40
        c_title = COLOR_D_POS if current_data['type'] == 'd' else COLOR_SP_POS
        screen.blit(font_huge.render(current_data['name'], True, c_title), (panel_x + 40, y_pos))
        y_pos += 80

        words = current_data['desc'].split(' ')
        line = ""
        for word in words:
            if font_medium.size(line + word)[0] > (WIDTH - panel_x - 80):
                color = (255, 200, 100) if "PRIMO" in line or "MEZI" in line or "UZLOVOU" in line else WHITE
                screen.blit(font_medium.render(line, True, color), (panel_x + 40, y_pos))
                y_pos += 35
                line = word + " "
            else:
                line += word + " "
        screen.blit(font_medium.render(line, True, WHITE), (panel_x + 40, y_pos))
        
        y_pos += 60
        pygame.draw.line(screen, (70, 80, 100), (panel_x + 40, y_pos), (WIDTH - 40, y_pos), 2)
        y_pos += 40

        screen.blit(font_large.render("Tajemstvi Oxidacnich Stavu", True, (150, 200, 255)), (panel_x + 40, y_pos))
        y_pos += 50
        
        exp_text = [
            "Proc prvky s/p bloku maji jen jeden hlavni stav,",
            "zatimco d-prvky (prechodne kovy) jich maji mnoho?",
            "",
            "U s/p prvku (napr. Sodik) ztratis 1 valencni elektron",
            "a narazis na stabilni elektronovou slupku jadra.",
            "Odebrat dalsi elektron z nizsiho patra vyzaduje",
            "neprekonatelne mnozstvi energie.",
            "",
            "U d-prvku (napr. Mangan) lezi valencni orbitaly",
            "4s a 3d energeticky TESNE NA SOBE. Priroda z nich",
            "muze odebirat elektrony postupne bez energetickych",
            "soku. Mangan tak muze mit stavy od +2 az do +7!"
        ]
        
        for line in exp_text:
            color = (255, 150, 150) if "neprekonatelne" in line else (COLOR_D_POS if "TESNE NA SOBE" in line else WHITE)
            screen.blit(font_medium.render(line, True, color), (panel_x + 40, y_pos))
            y_pos += 30

        y_pos += 40
        screen.blit(font_medium.render("Energeticka propast (s-blok) vs. Rovne patro (d-blok):", True, GRAY), (panel_x + 40, y_pos))
        y_pos += 40
        
        gx = panel_x + 60
        pygame.draw.rect(screen, (30, 35, 45), (gx, y_pos, 350, 160), border_radius=10)
        
        screen.blit(font_small.render("Sodik (s-blok)", True, WHITE), (gx + 30, y_pos + 15))
        pygame.draw.line(screen, COLOR_SP_POS, (gx + 30, y_pos + 60), (gx + 120, y_pos + 60), 4)
        screen.blit(font_tiny.render("3s (Valence)", True, COLOR_SP_POS), (gx + 40, y_pos + 45))
        pygame.draw.line(screen, (255, 100, 100), (gx + 30, y_pos + 140), (gx + 120, y_pos + 140), 4)
        screen.blit(font_tiny.render("2p (Stabilni jadro)", True, (255, 100, 100)), (gx + 20, y_pos + 145))
        pygame.draw.line(screen, WHITE, (gx + 75, y_pos + 65), (gx + 75, y_pos + 135), 2)
        screen.blit(font_tiny.render("Velky skok", True, WHITE), (gx + 85, y_pos + 95))

        screen.blit(font_small.render("Mangan (d-blok)", True, WHITE), (gx + 200, y_pos + 15))
        pygame.draw.line(screen, COLOR_SP_POS, (gx + 200, y_pos + 55), (gx + 290, y_pos + 55), 4)
        screen.blit(font_tiny.render("4s", True, COLOR_SP_POS), (gx + 300, y_pos + 48))
        pygame.draw.line(screen, COLOR_D_POS, (gx + 200, y_pos + 75), (gx + 290, y_pos + 75), 4)
        screen.blit(font_tiny.render("3d", True, COLOR_D_POS), (gx + 300, y_pos + 68))
        screen.blit(font_tiny.render("Blizko sebe =", True, WHITE), (gx + 210, y_pos + 105))
        screen.blit(font_tiny.render("Plynula oxidace", True, WHITE), (gx + 205, y_pos + 125))

        screen.blit(font_large.render("Zakladni (s, p, sp3)", True, COLOR_SP_POS), (60, HEIGHT - 170))
        screen.blit(font_large.render("Pokrocile (d)", True, COLOR_D_POS), (60, HEIGHT - 110))

        mx, my = pygame.mouse.get_pos()
        for i, btn in enumerate(buttons):
            is_d_btn = (ORBITALS[i]['type'] == 'd')
            base_color = COLOR_D_POS if is_d_btn else COLOR_SP_POS
            
            if current_idx == i:
                pygame.draw.rect(screen, base_color, btn, border_radius=8)
                txt_color = (20, 20, 20)
            elif btn.collidepoint(mx, my):
                pygame.draw.rect(screen, (80, 80, 100), btn, border_radius=8)
                txt_color = WHITE
            else:
                pygame.draw.rect(screen, (40, 45, 55), btn, border_radius=8)
                txt_color = GRAY
                pygame.draw.rect(screen, (60, 65, 75), btn, width=2, border_radius=8)
                
            txt = font_medium.render(ORBITALS[i]['name'], True, txt_color)
            screen.blit(txt, (btn.x + (btn_w - txt.get_width()) // 2, btn.y + 8))

        pygame.display.flip()
        clock.tick(60)
        
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())