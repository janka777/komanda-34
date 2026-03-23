# Skaitļu dalīšanas spēle

## Projekta apraksts

Šis projekts realizē divu spēlētāju skaitļu spēli, kuras pamatā ir skaitļa dalīšana un punktu uzskaite. Spēles gaitā spēlētāji pārmaiņus izdara gājienus, dalot tekošo skaitli ar 2, 3 vai 4, ja dalīšanas rezultātā iegūstams vesels skaitlis. Atkarībā no iegūtā rezultāta tiek mainīts spēlētāju punktu skaits. Spēles mērķis ir, izmantojot izdevīgākos gājienus, iegūt vairāk punktu nekā pretiniekam.

## Spēles sākums

Spēles sākumā programmatūra gadījuma ceļā saģenerē 5 skaitļus diapazonā no 20000 līdz 30000. Tiek izvēlēti tikai tādi skaitļi, kas dalās ar 2, 3 un 4. No piedāvātajiem skaitļiem cilvēks-spēlētājs izvēlas vienu skaitli, ar kuru tiek sākta spēle.

## Spēles gaita

Spēles sākumā abiem spēlētājiem ir 0 punktu. Spēlētāji izdara gājienus pārmaiņus. Katrā gājienā pašreizējo skaitli drīkst dalīt ar 2, 3 vai 4, bet tikai tad, ja rezultātā iegūstams vesels skaitlis.

Pēc katra gājiena tiek pārbaudīts iegūtais skaitlis:
- ja tas ir pāra skaitlis, pretiniekam tiek atņemts 1 punkts;
- ja tas ir nepāra skaitlis, pašreizējais spēlētājs iegūst 1 punktu.

## Spēles beigas

Spēle beidzas brīdī, kad tiek iegūts skaitlis, kas ir mazāks vai vienāds ar 10.

Pēc spēles beigām tiek salīdzināts abu spēlētāju punktu skaits:
- ja punktu skaits ir vienāds, rezultāts ir neizšķirts;
- ja punktu skaits atšķiras, uzvar spēlētājs ar lielāku punktu skaitu.

## Projekta mērķis

Projekta mērķis ir izveidot spēli, kurā iespējams modelēt gājienus, vērtēt to ietekmi uz rezultātu un noteikt uzvarētāju atbilstoši definētajiem noteikumiem.
