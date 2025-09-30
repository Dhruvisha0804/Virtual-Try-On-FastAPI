def insert_vto_tokens(
    conn, user_id, username, req_received_time, res_generated_time,
    response_id, input_prompt, text_tokens, image_tokens,
    prompt_tokens_total, revised_prompt, candidates_tokens, output_texts, gen_img_name
):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vto_Tokens_Gemini (
                user_id, username, req_received_time, responseId,
                input_prompt, textTokens, imageTokens,
                promptTokensTotal, revised_prompt, candidatesTokens,
                res_generated_time, outputTexts, gen_img_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, username, req_received_time, response_id,
            input_prompt, text_tokens, image_tokens,
            prompt_tokens_total, revised_prompt, candidates_tokens,
            res_generated_time, output_texts, gen_img_name
        ))

        conn.commit()
        cursor.close()

        return True, "Insert Successfully."

    except Exception as e:
        return False, str(e)