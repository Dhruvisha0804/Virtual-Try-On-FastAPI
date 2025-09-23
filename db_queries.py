def insert_vto_tokens(
        conn,
        user_id,
        username,
        req_received_time,
        res_generated_time,
        prompt_tokens=0,
        input_img_tokens=0,
        gen_img_name=None,
        gen_img_used_tokens=0
):

    try:
        cursor = conn.cursor()

        # user_id = 'dhruvisha19'
        # username = 'Dhruvisha Jaiswal'

        # user_id = user_id if user_id is not None else 'dhruvisha19'
        # username = username if username is not None else 'Dhruvisha Jaiswal'

        cursor.execute("""
            insert into vto_tokens (user_id, username, req_received_time, prompt_tokens, input_img_tokens, gen_img_name, res_generated_time, gen_img_used_tokens)
            values (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            username,
            req_received_time,
            prompt_tokens,
            input_img_tokens,
            gen_img_name,
            res_generated_time,
            gen_img_used_tokens
        ))

        conn.commit()
        cursor.close()

        return True, "Insert Successfully."

    except Exception as e:
        return False, str(e)
