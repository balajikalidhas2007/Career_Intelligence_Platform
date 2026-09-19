import styles from "./page.module.css";

export default function Home() {
  return (
    <>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.header__inner}>
          <div className={styles.header__logo}>
            <span className={styles["header__logo-icon"]}>⚡</span>
            Career Intelligence
          </div>
          <a href="http://localhost:8010/api/v1/auth/github" style={{ textDecoration: 'none' }}>
            <button className={styles.header__cta} id="header-sign-in">
              <svg
                className={styles["header__cta-icon"]}
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              Sign in with GitHub
            </button>
          </a>
        </div>
      </header>

      {/* Hero */}
      <section className={styles.hero} id="hero">
        <div className={`${styles.hero__glow} ${styles["hero__glow--primary"]}`} />
        <div className={`${styles.hero__glow} ${styles["hero__glow--secondary"]}`} />

        <div className={styles.hero__badge}>
          <span className={styles["hero__badge-dot"]} />
          Evidence-Based Career Intelligence
        </div>

        <h1 className={styles.hero__title}>
          Know Your Skills.
          <br />
          <span className={styles["hero__title-gradient"]}>Prove Your Worth.</span>
        </h1>

        <p className={styles.hero__subtitle}>
          Upload your resume, connect your GitHub, and let AI build a verified
          skill graph — then see exactly what you need to become job-ready.
        </p>

        <div className={styles.hero__actions}>
          <a href="http://localhost:8010/api/v1/auth/github" style={{ textDecoration: 'none' }}>
            <button className={`${styles.btn} ${styles["btn--primary"]}`} id="hero-get-started">
              Get Started — It&apos;s Free
            </button>
          </a>
          <button className={`${styles.btn} ${styles["btn--secondary"]}`} id="hero-learn-more">
            How It Works ↓
          </button>
        </div>
      </section>

      {/* Features */}
      <section className={styles.features} id="features">
        <div className={styles.features__header}>
          <p className={styles.features__label}>Core Features</p>
          <h2 className={styles.features__title}>
            Skills Backed by Evidence, Not Keywords
          </h2>
          <p className={styles.features__subtitle}>
            We don&apos;t just match resume words to job descriptions. We analyze
            your actual work to build a verified skill profile.
          </p>
        </div>

        <div className={styles.features__grid}>
          <div className={styles["feature-card"]}>
            <div className={`${styles["feature-card__icon"]} ${styles["feature-card__icon--indigo"]}`}>
              📄
            </div>
            <h3 className={styles["feature-card__title"]}>Resume Intelligence</h3>
            <p className={styles["feature-card__description"]}>
              Upload your resume and our AI extracts skills with evidence — not
              just keywords, but the context that proves your competency.
            </p>
          </div>

          <div className={styles["feature-card"]}>
            <div className={`${styles["feature-card__icon"]} ${styles["feature-card__icon--cyan"]}`}>
              🔗
            </div>
            <h3 className={styles["feature-card__title"]}>GitHub Analysis</h3>
            <p className={styles["feature-card__description"]}>
              Connect your GitHub and we analyze your repositories — languages,
              frameworks, patterns, and project complexity become evidence.
            </p>
          </div>

          <div className={styles["feature-card"]}>
            <div className={`${styles["feature-card__icon"]} ${styles["feature-card__icon--violet"]}`}>
              🎯
            </div>
            <h3 className={styles["feature-card__title"]}>Evidence-Aware Gap Analysis</h3>
            <p className={styles["feature-card__description"]}>
              Compare your verified skills against real role requirements.
              See not just what you&apos;re missing, but how to build proof.
            </p>
          </div>

          <div className={styles["feature-card"]}>
            <div className={`${styles["feature-card__icon"]} ${styles["feature-card__icon--emerald"]}`}>
              🗺️
            </div>
            <h3 className={styles["feature-card__title"]}>Actionable Roadmap</h3>
            <p className={styles["feature-card__description"]}>
              Get personalized recommendations — projects to build, courses to
              take, and contributions to make — that create new evidence.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works (The Loop) */}
      <section className={styles.loop} id="how-it-works">
        <div className={styles.loop__header}>
          <p className={styles.loop__label}>How It Works</p>
          <h2 className={styles.loop__title}>The Evidence Feedback Loop</h2>
          <p className={styles.loop__subtitle}>
            A continuous cycle that turns your work into proof of competency.
          </p>
        </div>

        <div className={styles.loop__steps}>
          <div className={styles["loop-step"]}>
            <span className={styles["loop-step__number"]}>1</span>
            <div className={styles["loop-step__content"]}>
              <p className={styles["loop-step__title"]}>Submit Your Evidence</p>
              <p className={styles["loop-step__description"]}>
                Upload a resume or connect your GitHub repositories
              </p>
            </div>
          </div>

          <div className={styles["loop-step__arrow"]}>↓</div>

          <div className={styles["loop-step"]}>
            <span className={styles["loop-step__number"]}>2</span>
            <div className={styles["loop-step__content"]}>
              <p className={styles["loop-step__title"]}>AI Extracts Your Skills</p>
              <p className={styles["loop-step__description"]}>
                Skills are identified with evidence excerpts and proficiency assessment
              </p>
            </div>
          </div>

          <div className={styles["loop-step__arrow"]}>↓</div>

          <div className={styles["loop-step"]}>
            <span className={styles["loop-step__number"]}>3</span>
            <div className={styles["loop-step__content"]}>
              <p className={styles["loop-step__title"]}>View Your Skill Graph</p>
              <p className={styles["loop-step__description"]}>
                See all your skills, confidence levels, and the evidence backing each one
              </p>
            </div>
          </div>

          <div className={styles["loop-step__arrow"]}>↓</div>

          <div className={styles["loop-step"]}>
            <span className={styles["loop-step__number"]}>4</span>
            <div className={styles["loop-step__content"]}>
              <p className={styles["loop-step__title"]}>Compare Against Target Roles</p>
              <p className={styles["loop-step__description"]}>
                Select a career target and see evidence-aware skill gaps
              </p>
            </div>
          </div>

          <div className={styles["loop-step__arrow"]}>↓</div>

          <div className={styles["loop-step"]}>
            <span className={styles["loop-step__number"]}>5</span>
            <div className={styles["loop-step__content"]}>
              <p className={styles["loop-step__title"]}>Act on Recommendations</p>
              <p className={styles["loop-step__description"]}>
                Build projects, take courses, contribute — then submit new evidence and repeat
              </p>
            </div>
          </div>

          <div className={styles["loop-step__arrow"]}>🔄</div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <p className={styles.footer__text}>
          Career Intelligence Platform — Evidence-based career guidance powered by AI
        </p>
      </footer>
    </>
  );
}
