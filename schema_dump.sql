SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
ALTER SCHEMA public OWNER TO twilio;
SET default_tablespace = '';
SET default_table_access_method = heap;
CREATE TABLE public.messages (
    tel character varying(20),
    sent timestamp without time zone,
    is_user boolean,
    body text
);
ALTER TABLE public.messages OWNER TO twilio;
CREATE TABLE public.purchase_offers (
    unique_id uuid NOT NULL,
    tel character varying(20) NOT NULL,
    offer_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_used boolean DEFAULT false NOT NULL
);
ALTER TABLE public.purchase_offers OWNER TO twilio;
CREATE TABLE public.purchases (
    tel character varying(20),
    purchase_date timestamp without time zone,
    purchase_type character varying(50),
    message_count integer
);
ALTER TABLE public.purchases OWNER TO twilio;
ALTER TABLE ONLY public.purchase_offers
    ADD CONSTRAINT purchase_offers_pkey PRIMARY KEY (unique_id);
CREATE INDEX messages_tel ON public.messages USING btree (tel);
ALTER TABLE public.messages CLUSTER ON messages_tel;
CREATE INDEX purchases_tel ON public.purchases USING btree (tel);
