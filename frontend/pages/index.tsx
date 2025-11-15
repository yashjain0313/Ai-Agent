import Head from "next/head";
import ResumeUpload from "@/components/ResumeUpload";

export default function Home() {
  return (
    <>
      <Head>
        <title>AI Job Search Platform</title>
        <meta
          name="description"
          content="Upload your resume and find perfect jobs with AI"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <ResumeUpload />
    </>
  );
}
