export default function LanguageSwitcher({ lang, onChange }) {
  const next = lang === 'hu' ? 'en' : 'hu';
  const label = lang === 'hu' ? 'EN' : 'HU';

  return (
    <div className="lang-switcher">
      <button className="lang-btn" onClick={() => onChange(next)}>
        {label}
      </button>
    </div>
  );
}
