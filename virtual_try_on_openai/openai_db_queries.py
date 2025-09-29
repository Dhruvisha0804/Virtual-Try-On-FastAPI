def insert_vto_tokens_openai(
        conn,
        user_id,
        username,
        main_id,
        input_prompt,
        input_text_prompt_tokens,
        output_format,
        quality,
        revised_prompt,
        gen_img_size,
        resp_id,
        resp_text,
        input_total_tokens,
        output_text_tokens,
        total_tokens,
        req_received_time=None,
        res_generated_time=None
):

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO vto_Tokens_openAI 
            (user_id, username, req_received_time, main_id, input_prompt, input_text_prompt_tokens, 
             output_format, quality, revised_prompt, gen_img_size, resp_id, resp_text, 
             input_total_tokens, output_text_tokens, total_tokens, res_generated_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            username,
            req_received_time,
            main_id,
            input_prompt,
            input_text_prompt_tokens,
            output_format,
            quality,
            revised_prompt,
            gen_img_size,
            resp_id,
            resp_text,
            input_total_tokens,
            output_text_tokens,
            total_tokens,
            res_generated_time
        ))

        conn.commit()
        cursor.close()

        return True, "Insert Successfully."

    except Exception as e:
        return False, str(e)
