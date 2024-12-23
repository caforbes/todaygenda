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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: daylists; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.daylists (
    id integer NOT NULL,
    user_id integer NOT NULL,
    expiry timestamp with time zone NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: daylists_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.daylists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: daylists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.daylists_id_seq OWNED BY public.daylists.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    done boolean DEFAULT false NOT NULL,
    estimate interval,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone,
    finished_at timestamp without time zone,
    daylist_id integer NOT NULL,
    daylist_order integer,
    CONSTRAINT check_done_task_has_finishtime CHECK (((NOT done) OR (finished_at IS NOT NULL))),
    CONSTRAINT check_done_tasks_unordered CHECK (((daylist_order IS NULL) OR (done = false))),
    CONSTRAINT check_pending_tasks_ordered CHECK (((daylist_order IS NOT NULL) OR (done = true))),
    CONSTRAINT check_undone_task_no_finishtime CHECK ((done OR (finished_at IS NULL)))
);


--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(254),
    password_hash character varying(100),
    registered_at timestamp without time zone,
    CONSTRAINT check_registered_user_data CHECK ((((email IS NULL) AND (password_hash IS NULL) AND (registered_at IS NULL)) OR ((email IS NOT NULL) AND (password_hash IS NOT NULL) AND (registered_at IS NOT NULL))))
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: daylists id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daylists ALTER COLUMN id SET DEFAULT nextval('public.daylists_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: daylists daylists_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daylists
    ADD CONSTRAINT daylists_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: users unique_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_email UNIQUE (email);


--
-- Name: tasks unique_task_order_in_daylist; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT unique_task_order_in_daylist UNIQUE (daylist_id, daylist_order);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: daylists daylists_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daylists
    ADD CONSTRAINT daylists_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_daylist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_daylist_id_fkey FOREIGN KEY (daylist_id) REFERENCES public.daylists(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20240824004320'),
    ('20240828065735'),
    ('20240909225518'),
    ('20240926232413'),
    ('20241015180043');
