interface Props {
  title: string;
  text: string;
}

export default function ComingSoonPage({ title, text }: Props) {
  return (
    <div className="py-16 text-center">
      <h1 className="text-2xl font-extrabold">{title}</h1>
      <p className="mt-2 text-stone-600 dark:text-stone-300">{text}</p>
      <p className="mt-6 inline-block rounded-full bg-stone-200 px-4 py-1 text-sm font-bold dark:bg-stone-800">
        Em breve
      </p>
    </div>
  );
}
