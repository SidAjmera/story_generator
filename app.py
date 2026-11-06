import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64

load_dotenv()
client=OpenAI()

def create_story(storyprompt, agegroup, length):
    prompt = f"""
Create a story about {storyprompt}. 
The age group for this story should be {agegroup}. 
Make the story {length} paragraph(s) long.
"""

    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt,
    )
    return response.output_text

def generate_summary(story):
    prompt = f"""
Create a summary of this story: {story}
Make it 6 sentences long, simple yet detailed enough to be able to generate an image with it. 
"""

    response = client.responses.create(
        model="gpt-4o",
        input=story,
    )
    return response.output_text

def generate_image(story, agegroup, images, image_type):
    image_prompt = f"""
Take this story: {story}, and generate a accompanying image for it without any text. 
The images should be in a style meant for {agegroup} age group. 
Create the image with a {image_type} style. 
Do not make it a comic book strip style image or multiple sub images in the main image, make a single representative image. Make the image with a 4:3 aspect ratio.
"""
    result = client.images.generate(
        model="gpt-image-2.6-flare", prompt=image_prompt, size="1024x1024", quality="medium"
    )
    return base64.b64decode(result.data[0].b64_json)

st.set_page_config(page_title="AI Story Generator", page_icon="📚", layout="wide")
st.title("📚 AI Story Generator")
st.write("Create personalized stories with custom images.")
col1, col2 = st.columns(2)
storyprompt = col1.text_area("What would you like your story to be about?", placeholder="Example: A story about a dog who can talk.")
agegroup = col2.selectbox("Select age group:", ["Elementary (6-11)", "Middle School [12-14]", "High School[15-18]"])
genre = col2.selectbox("Select genre:", ["Fantasy", "Adventure", "Mystery", "Comedy", "Romance", "Realistic"])
image_type = st.selectbox("Select type of image(s):", ["Retro", "Comic", "Realistic", "Manga", "B&W"])
length = st.slider("How many paragraphs should the story be?", max_value=15, step=1)
images = st.slider("How many images should the story have?", max_value=5, step=1)
with st.expander("💡Need some inspiration?"):
    st.write("Here are 5 story ideas to get you started!")
    st.markdown("""
- A shy dragon who is afraid of fire starts their first day at school.
- A child discovers that their pet cat secretly protects the neighbourhood at night.
- Two friends find a library where every book opens a doorway into its story.
- A tiny robot sets out to grow the first flower on the Moon.
- A dog gains the ability to talk, but only when nobody else is listening.
""")
create = st.button("Generate Story")
if create:
    with st.spinner("Generating your story..."):
        story = create_story(storyprompt, agegroup, length)
        st.markdown(story)

    with st.spinner("Generating a summary..."):
        generation_prompt = generate_summary(story)
        with st.expander("Want to see the info given to the image generation model?"):
            st.write(f"""
Story summary: {generation_prompt}
Age group: {agegroup}
Image type: {image_type}
""")


    with st.spinner("Generating your image..."):
        image_data = generate_image(generation_prompt, agegroup, images, image_type)
        st.image(image_data)
        image_b64 = base64.b64encode(image_data).decode()
        paragraphs = "".join(f"<p>{p}</p>" for p in story.split("\n\n"))
        html = f"""<html><head><meta charset="UTF-8"><title>My AI Story</title></head><body style='font-family:Arial;max-width:700px;margin:40px auto;font-size:18px;line-height:1.6'><h1>My AI Story</h1><img src='data:image/png;base64,{image_b64}' style='width:100%;border-radius:10px'>{paragraphs}</body></html>"""
        st.download_button(
            "Download Story as HTML", data=html,
            file_name="my_story.html", mime="text/html",
            on_click="ignore"
        )