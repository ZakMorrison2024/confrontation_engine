import pygame
import random
import openai
import time
import sys

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 600
FPS = 30
FONT = pygame.font.SysFont('Arial', 24)
INPUT_FONT = pygame.font.SysFont('Arial', 20)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Define basic confrontation scenarios
scenarios = {
    'public': [
        'You are being publicly criticized at work for something you didn’t do.',
        'Someone cuts in front of you in a long queue at the store and makes a rude comment.',
        'A stranger aggressively confronts you about a minor accident you were involved in.'
    ],
    'spouse': [
        'Your partner accuses you of neglecting them due to your work schedule.',
        'Your spouse is upset because you forgot an important anniversary.',
        'You and your partner disagree about a major life decision (e.g., moving cities, finances).'
    ],
    'parent': [
        'Your mother/father is upset because they feel you’ve distanced yourself from the family.',
        'Your parent is angry with you for making a decision they don’t agree with (e.g., career choice).',
        'Your father/mother disapproves of your relationship with someone you care about.'
    ]
}

# Define severity levels for responses
response_strategies = {
    'low_severity': ['Avoid the confrontation', 'Ignore the issue', 'Calmly walk away'],
    'medium_severity': ['Calmly explain your side', 'Ask them to explain their perspective', 'Use humor to defuse the tension'],
    'high_severity': ['Stand your ground firmly', 'Ask for a timeout to cool down', 'Use logical reasoning and provide evidence']
}

# Define intellectual capacities for responses
intellectual_strategies = {
    'low': ['Emotional response', 'Escalate the confrontation', 'Defensive stance'],
    'medium': ['Calm reasoning', 'Empathize with their position', 'Use examples to illustrate your point'],
    'high': ['Provide clear, factual arguments', 'Break down the issue logically', 'Focus on resolution and finding common ground']
}

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Confrontation Simulator")
clock = pygame.time.Clock()


def wrap_text(text, font, max_width):
    # Split the text into words
    words = text.split(' ')
    lines = []
    current_line = ''
    
    for word in words:
        # Check if adding the word would exceed the max_width
        test_line = current_line + ' ' + word if current_line else word
        test_width, _ = font.size(test_line)
        
        if test_width <= max_width:
            # If it fits, add the word to the current line
            current_line = test_line
        else:
            # If it doesn't fit, start a new line
            if current_line:
                lines.append(current_line)
            current_line = word
    
    # Add the last line
    if current_line:
        lines.append(current_line)
    
    return lines

# GPT Analysis function (Optional)
def gpt_analysis(confrontation,response):
    openai.api_key = 'your-api-key-here'  # Replace with your OpenAI API key
    prompt = f"Analyze the following confrontation {confrontation} and responses:\nUser's response: {response}\nPlease provide a score out of 10 and explain how well the user handled the confrontation."
    
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        gpt_output = response.choices[0].text.strip()
        return gpt_output
    
    except Exception as e:
        return f"Error communicating with GPT API: {e}"

# Main menu function
def main_menu():
    selected_option = None
    buttons = [
        ('Start Simulation', pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 100, 200, 50)),
        ('Quit', pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)),
    ]

    while selected_option is None:
        screen.fill(WHITE)
        for button_text, rect in buttons:
            pygame.draw.rect(screen, BLUE, rect)
            text = FONT.render(button_text, True, WHITE)
            screen.blit(text, (rect[0] + 20, rect[1] + 15))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if buttons[0][1].collidepoint(mouse_pos):
                    selected_option = 'start'
                elif buttons[1][1].collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

def get_user_input(prompt, font, max_width, scenario, height_offset=100):
    input_text = ''
    active = True
    cursor_visible = True
    cursor_timer = time.time()
    
    while active:
        # Clear the screen for input area only
        screen.fill(WHITE)
        
        # Display the scenario (this stays visible)
        wrapped_scenario = wrap_text(scenario, FONT, max_width)
        
        y_offset = 50
        for line in wrapped_scenario:
            scenario_text = FONT.render(line, True, BLACK)
            screen.blit(scenario_text, (20, y_offset))
            y_offset += FONT.get_height() + 5  # Space between lines
        
        # Display the prompt
        prompt_text = font.render(prompt, True, BLACK)
        screen.blit(prompt_text, (20, height_offset + 20))
        
        # Display the user input
        input_text_display = font.render(input_text, True, BLACK)
        screen.blit(input_text_display, (20, height_offset + 60))
        
        # Display cursor
        if cursor_visible:
            pygame.draw.line(screen, BLACK, (20 + input_text_display.get_width(), height_offset + 60),
                             (20 + input_text_display.get_width(), height_offset + 60 + input_text_display.get_height()), 2)
        
        # Handle user input
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # When Enter is pressed, finish input
                    active = False
                elif event.key == pygame.K_BACKSPACE:  # Handle backspace to remove last character
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode  # Add character to input_text
        
        # Toggle cursor visibility every 0.5 seconds
        if time.time() - cursor_timer >= 0.5:
            cursor_visible = not cursor_visible
            cursor_timer = time.time()
        
        clock.tick(FPS)
    
    return input_text

# Function to handle the confrontation with user input
def handle_confrontation(scenario_type, severity, intellectual_capacity, gpt_enabled):
    screen.fill(WHITE)

    # Randomly choose scenario and options
    scenario = random.choice(scenarios[scenario_type])

    # Wrap the scenario text
    wrapped_scenario = wrap_text(scenario, FONT, 760)  # Padding for edges

    # Display the scenario
    y_offset = 50
    for line in wrapped_scenario:
        scenario_text = FONT.render(line, True, BLACK)
        screen.blit(scenario_text, (20, y_offset))
        y_offset += FONT.get_height() + 5  # Space between lines
    
    # Allow user to input their response
    response = get_user_input("Enter your response:", INPUT_FONT, 760,scenario, y_offset)
    pygame.display.update()

    # If GPT is enabled, analyze the responses
    if gpt_enabled:
        gpt_output = "This is GPT feedback based on the user's response."
        gpt_text = FONT.render(f"GPT Feedback: {gpt_output}", True, BLACK)
        screen.blit(gpt_text, (20, 400))
        pygame.display.flip()
        time.sleep(5)  # Wait to show the feedback
        

    time.sleep(1)  # Wait for a moment before going back to the main menu

# Main function
def main():
    main_menu()
    
    # Choose GPT toggle and confrontation options
    gpt_enabled = False # Enable GPT analysis for this session, can be set based on user input
    
    scenario_type = 'public'  # This could be selected based on user input
    severity = 'medium_severity'  # This could be selected based on user input
    intellectual_capacity = 'high'  # This could be selected based on user input
    
    handle_confrontation(scenario_type, severity, intellectual_capacity, gpt_enabled)

# Run the program
if __name__ == "__main__":
    main()
